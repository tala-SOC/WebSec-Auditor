from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.scanner.headers import scan_headers
from backend.scanner.cookies import scan_cookies


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="WebSec Auditor",
    description="Lightweight web security auditing tool",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


# ============================================================
# MODELS
# ============================================================

class ScanRequest(BaseModel):
    url: str


# ============================================================
# URL VALIDATION
# ============================================================

def validate_url(url: str) -> str:

    url = url.strip()

    if not url:
        raise HTTPException(
            status_code=400,
            detail="URL is required."
        )

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


# ============================================================
# FRONTEND ROUTES
# ============================================================

@app.get("/")
def frontend():
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


@app.get("/results")
def results():
    return FileResponse(
        FRONTEND_DIR / "results.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "online",
        "service": "WebSec Auditor"
    }


# ============================================================
# HEADER SCAN
# ============================================================

@app.post("/scan/headers")
def scan_headers_endpoint(request: ScanRequest):

    url = validate_url(request.url)

    return {
        "url": url,
        "findings": scan_headers(url)
    }


# ============================================================
# COOKIE SCAN
# ============================================================

@app.post("/scan/cookies")
def scan_cookies_endpoint(request: ScanRequest):

    url = validate_url(request.url)

    return {
        "url": url,
        "findings": scan_cookies(url)
    }


# ============================================================
# FULL SECURITY SCAN
# ============================================================

@app.post("/scan")
def full_scan(request: ScanRequest):

    url = validate_url(request.url)

    all_findings = []


    # --------------------------------------------------------
    # Security Headers
    # --------------------------------------------------------

    header_findings = scan_headers(url)
    all_findings.extend(header_findings)


    # --------------------------------------------------------
    # Cookies
    # --------------------------------------------------------

    cookie_findings = scan_cookies(url)
    all_findings.extend(cookie_findings)

    # ========================================================
    # SCORE
    # ========================================================

    score = 100

    for finding in all_findings:

        if finding["status"] in ["MISSING", "ERROR"]:

            severity = finding["severity"]

            if severity == "HIGH":
                score -= 20

            elif severity == "MEDIUM":
                score -= 10

            elif severity == "LOW":
                score -= 5


    # Keep score between 0 and 100

    score = max(0, min(100, score))


    # ========================================================
    # SUMMARY
    # ========================================================

    passed = sum(
        1
        for finding in all_findings
        if finding["status"] == "PASS"
    )

    issues = sum(
        1
        for finding in all_findings
        if finding["status"] in ["MISSING", "ERROR"]
    )

    high = sum(
        1
        for finding in all_findings
        if finding["status"] in ["MISSING", "ERROR"]
        and finding["severity"] == "HIGH"
    )

    medium = sum(
        1
        for finding in all_findings
        if finding["status"] in ["MISSING", "ERROR"]
        and finding["severity"] == "MEDIUM"
    )

    low = sum(
        1
        for finding in all_findings
        if finding["status"] in ["MISSING", "ERROR"]
        and finding["severity"] == "LOW"
    )


    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "url": url,

        "score": score,

        "summary": {
            "total": len(all_findings),
            "passed": passed,
            "issues": issues,
            "high": high,
            "medium": medium,
            "low": low
        },

        "findings": all_findings
    }