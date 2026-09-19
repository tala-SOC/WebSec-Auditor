import requests


SECURITY_HEADERS = {
    "Content-Security-Policy": {
        "severity": "MEDIUM",
        "description": "Content Security Policy header is missing.",
        "recommendation": "Configure a suitable Content-Security-Policy header."
    },
    "X-Frame-Options": {
        "severity": "MEDIUM",
        "description": "X-Frame-Options header is missing.",
        "recommendation": "Set X-Frame-Options to DENY or SAMEORIGIN."
    },
    "X-Content-Type-Options": {
        "severity": "LOW",
        "description": "X-Content-Type-Options header is missing.",
        "recommendation": "Set X-Content-Type-Options to nosniff."
    },
    "Strict-Transport-Security": {
        "severity": "MEDIUM",
        "description": "HSTS header is missing.",
        "recommendation": "Enable HTTP Strict Transport Security for HTTPS websites."
    },
    "Referrer-Policy": {
        "severity": "LOW",
        "description": "Referrer-Policy header is missing.",
        "recommendation": "Configure an appropriate Referrer-Policy."
    },
    "Permissions-Policy": {
        "severity": "LOW",
        "description": "Permissions-Policy header is missing.",
        "recommendation": "Configure Permissions-Policy to restrict unnecessary browser features."
    }
}


def scan_headers(url: str):
    findings = []

    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True
        )

        headers = response.headers

        for header, info in SECURITY_HEADERS.items():

            if header in headers:
                findings.append({
                    "name": header,
                    "status": "PASS",
                    "severity": "INFO",
                    "description": f"{header} is present.",
                    "recommendation": None
                })

            else:
                findings.append({
                    "name": header,
                    "status": "MISSING",
                    "severity": info["severity"],
                    "description": info["description"],
                    "recommendation": info["recommendation"]
                })

        return findings

    except requests.RequestException as error:

        return [{
            "name": "Security Headers",
            "status": "ERROR",
            "severity": "HIGH",
            "description": f"Unable to connect to the target website: {error}",
            "recommendation": "Verify that the URL is reachable and try again."
        }]