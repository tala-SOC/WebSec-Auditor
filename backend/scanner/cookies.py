import requests


def scan_cookies(url: str):
    findings = []

    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True
        )

        cookies = response.cookies

        if not cookies:
            return [{
                "name": "Cookies",
                "status": "INFO",
                "severity": "INFO",
                "description": "No cookies were set by the server.",
                "recommendation": None
            }]

        for cookie in cookies:

            # Secure
            if cookie.secure:
                findings.append({
                    "name": f"{cookie.name} - Secure",
                    "status": "PASS",
                    "severity": "INFO",
                    "description": "Cookie is configured with the Secure attribute.",
                    "recommendation": None
                })
            else:
                findings.append({
                    "name": f"{cookie.name} - Secure",
                    "status": "MISSING",
                    "severity": "MEDIUM",
                    "description": "Cookie does not have the Secure attribute.",
                    "recommendation": "Enable the Secure attribute so the cookie is only sent over HTTPS."
                })

            # HttpOnly
            if cookie.has_nonstandard_attr("HttpOnly"):
                findings.append({
                    "name": f"{cookie.name} - HttpOnly",
                    "status": "PASS",
                    "severity": "INFO",
                    "description": "Cookie is configured with the HttpOnly attribute.",
                    "recommendation": None
                })
            else:
                findings.append({
                    "name": f"{cookie.name} - HttpOnly",
                    "status": "MISSING",
                    "severity": "MEDIUM",
                    "description": "Cookie does not have the HttpOnly attribute.",
                    "recommendation": "Enable HttpOnly to reduce the risk of client-side scripts accessing the cookie."
                })

        return findings

    except requests.RequestException as error:

        return [{
            "name": "Cookies",
            "status": "ERROR",
            "severity": "HIGH",
            "description": f"Unable to analyze cookies: {error}",
            "recommendation": "Verify that the URL is reachable and try again."
        }]