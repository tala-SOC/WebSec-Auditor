import requests
 
 
def _finding(name, status, severity, description, recommendation=None):
    return {
        "name": name,
        "status": status,
        "severity": severity,
        "description": description,
        "recommendation": recommendation,
    }
 
 
def scan_cookies(url: str):
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
 
        # نقرأ Set-Cookie الخام من كل خطوات التحويل، مو من الرد الأخير فقط
        raw_cookies = []
        for r in [*response.history, response]:
            raw_cookies += r.raw.headers.getlist("Set-Cookie")
 
        if not raw_cookies:
            return [_finding("Cookies", "INFO", "INFO",
                             "No cookies were set by the server.")]
 
        findings = []
 
        for raw in raw_cookies:
            parts = [p.strip() for p in raw.split(";")]
            name = parts[0].split("=", 1)[0]
            flags = {p.split("=", 1)[0].lower() for p in parts[1:]}   # مقارنة بدون حساسية للحروف
 
            if "secure" in flags:
                findings.append(_finding(f"{name} - Secure", "PASS", "INFO",
                                         "Cookie is configured with the Secure attribute."))
            else:
                findings.append(_finding(
                    f"{name} - Secure", "MISSING", "MEDIUM",
                    "Cookie does not have the Secure attribute.",
                    "Enable the Secure attribute so the cookie is only sent over HTTPS."))
 
            if "httponly" in flags:
                findings.append(_finding(f"{name} - HttpOnly", "PASS", "INFO",
                                         "Cookie is configured with the HttpOnly attribute."))
            else:
                findings.append(_finding(
                    f"{name} - HttpOnly", "MISSING", "MEDIUM",
                    "Cookie does not have the HttpOnly attribute.",
                    "Enable HttpOnly to reduce the risk of client-side scripts reading the cookie."))
 
        return findings
 
    except requests.RequestException as error:
        return [_finding("Cookies", "ERROR", "HIGH",
                         f"Unable to analyze cookies: {error}",
                         "Verify that the URL is reachable and try again.")]
 