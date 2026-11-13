import ipaddress
import socket
from pathlib import Path
from urllib.parse import urlparse
 
import requests
import fastapi
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
 
# المسارات تُحسب من مكان هذا الملف، فما تتأثر بمكان تشغيلك للتيرمنال
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
 
print("Static folder   :", STATIC_DIR)
print("Templates folder:", TEMPLATES_DIR)
 
app = fastapi.FastAPI(title="WebSec Auditor")
 
 
# ---------- منع الكاش أثناء التطوير ----------
 
NO_CACHE = {"Cache-Control": "no-store"}
 
 
class NoCacheStatic(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store"
        return response
 
 
app.mount("/static", NoCacheStatic(directory=STATIC_DIR), name="static")
 
 
# ---------- الصفحات ----------
 
@app.get("/")
def index():
    return FileResponse(TEMPLATES_DIR / "index.html", headers=NO_CACHE)
 
 
@app.get("/results")
def results():
    # غيّري الاسم إذا ملفك اسمه result.html
 return FileResponse(TEMPLATES_DIR / "result.html", headers=NO_CACHE)
 
 
# ---------- الفحص ----------
 
class ScanRequest(BaseModel):
    url: str
 
 
SECURITY_HEADERS = [
    ("Strict-Transport-Security", "HIGH",
     "Forces browsers to use HTTPS only.",
     "Add: Strict-Transport-Security: max-age=31536000; includeSubDomains"),
    ("Content-Security-Policy", "HIGH",
     "Limits where scripts and resources can load from, reducing XSS risk.",
     "Define a Content-Security-Policy that allows only trusted sources."),
    ("X-Frame-Options", "MEDIUM",
     "Protects against clickjacking by controlling framing.",
     "Add: X-Frame-Options: DENY (or use CSP frame-ancestors)."),
    ("X-Content-Type-Options", "MEDIUM",
     "Stops browsers from guessing content types (MIME sniffing).",
     "Add: X-Content-Type-Options: nosniff"),
    ("Referrer-Policy", "LOW",
     "Controls how much referrer information is shared.",
     "Add: Referrer-Policy: strict-origin-when-cross-origin"),
    ("Permissions-Policy", "LOW",
     "Restricts access to browser features like camera and location.",
     "Add a Permissions-Policy header limiting unused features."),
]
 
PENALTY = {"HIGH": 15, "MEDIUM": 8, "LOW": 4}
 
 
def normalize_url(raw: str) -> str:
    raw = raw.strip()
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
 
    parsed = urlparse(raw)
    if not parsed.hostname:
        raise fastapi.HTTPException(status_code=400, detail="Invalid URL.")
 
    # منع فحص عناوين داخلية (حماية من SSRF)
    try:
        for info in socket.getaddrinfo(parsed.hostname, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise fastapi.HTTPException(
                    status_code=400,
                    detail="Scanning local or private addresses is not allowed.",
                )
    except socket.gaierror:
        raise fastapi.HTTPException(status_code=400, detail="Could not resolve this domain.")
 
    return raw
 
 
def finding(name, status, severity, description, recommendation=None):
    return {
        "name": name,
        "status": status,          # PASS | MISSING | ERROR
        "severity": severity,      # HIGH | MEDIUM | LOW
        "description": description,
        "recommendation": recommendation,
    }
 
 
@app.post("/scan")
def scan(req: ScanRequest):
    url = normalize_url(req.url)
 
    try:
        r = requests.get(
            url,
            timeout=10,
            allow_redirects=True,
            headers={
                "User-Agent": "WebSecAuditor/1.0",
                "Origin": "https://evil.example",   # لاختبار سياسة CORS
            },
        )
    except requests.RequestException as e:
        raise fastapi.HTTPException(status_code=502, detail=f"Could not reach the website: {e.__class__.__name__}")
 
    findings = []
 
    # --- HTTPS ---
    if r.url.startswith("https://"):
        findings.append(finding("HTTPS", "PASS", "HIGH", "The site is served over HTTPS."))
    else:
        findings.append(finding(
            "HTTPS", "MISSING", "HIGH",
            "The site is served over plain HTTP, so traffic can be read or modified.",
            "Enable HTTPS with a valid certificate and redirect all HTTP traffic to it."))
 
    # --- Security headers ---
    for header, severity, desc, rec in SECURITY_HEADERS:
        if header in r.headers:
            findings.append(finding(header, "PASS", severity, desc))
        else:
            findings.append(finding(header, "MISSING", severity,
                                    f"{header} header is missing. {desc}", rec))
 
    # --- Cookies ---
    cookies = r.raw.headers.getlist("Set-Cookie") if hasattr(r.raw.headers, "getlist") else []
    if not cookies:
        findings.append(finding("Cookies", "PASS", "LOW", "No cookies were set on the first response."))
    else:
        for c in cookies:
            cname = c.split("=", 1)[0].strip()
            low = c.lower()
            missing = [flag for flag, key in (("Secure", "secure"), ("HttpOnly", "httponly")) if key not in low]
            if missing:
                findings.append(finding(
                    f"Cookie: {cname}", "MISSING", "MEDIUM",
                    f"Cookie is missing: {', '.join(missing)}.",
                    "Set the Secure and HttpOnly attributes on session cookies."))
            else:
                findings.append(finding(f"Cookie: {cname}", "PASS", "MEDIUM",
                                        "Cookie has Secure and HttpOnly set."))
 
    # --- CORS ---
    acao = r.headers.get("Access-Control-Allow-Origin")
    if acao in ("*", "https://evil.example"):
        findings.append(finding(
            "CORS", "MISSING", "HIGH",
            f"The site allows cross-origin requests from untrusted origins (Allow-Origin: {acao}).",
            "Restrict Access-Control-Allow-Origin to a specific list of trusted origins."))
    else:
        findings.append(finding("CORS", "PASS", "HIGH", "No unsafe CORS policy was detected."))
 
    # --- Information leakage ---
    leaks = [h for h in ("Server", "X-Powered-By", "X-AspNet-Version") if h in r.headers]
    if leaks:
        shown = ", ".join(f"{h}: {r.headers[h]}" for h in leaks)
        findings.append(finding(
            "Information Leakage", "MISSING", "LOW",
            f"The server reveals technology details ({shown}).",
            "Remove or hide version information from response headers."))
    else:
        findings.append(finding("Information Leakage", "PASS", "LOW",
                                "No server or technology details were exposed in headers."))
 
    # --- Score ---
    score = 100
    for f in findings:
        if f["status"] != "PASS":
            score -= PENALTY.get(f["severity"], 0)
 
    return {"url": r.url, "score": max(score, 0), "findings": findings}
 