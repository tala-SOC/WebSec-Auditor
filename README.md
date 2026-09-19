# WebSec Auditor

WebSec Auditor is a lightweight web security auditing tool that checks a website for common security misconfigurations and generates a clear security report.

## Features

- Security Headers Analysis
- Cookie Security Checks
- CORS Configuration Analysis
- Information Leakage Detection
- Security Score
- Severity Classification
- Security Recommendations

## Tech Stack

### Backend
- Python
- FastAPI
- Requests
- Pydantic

### Frontend
- HTML5
- CSS3
- JavaScript

## Project Structure

```text
WebSec-Auditor/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── scanner/
│   │   ├── __init__.py
│   │   ├── headers.py
│   │   └── cookies.py
│   └── models/
│       ├── __init__.py
│       └── results.py
│
├── frontend/
│   ├── index.html
│   ├── results.html
│   ├── style.css
│   └── app.js
│
├── .gitignore
└── README.md
How It Works
Enter a website URL.
WebSec Auditor sends an HTTP request to the target.
The application analyzes the returned security configuration.
Findings are classified by severity.
A security score and recommendations are generated.
Running Locally
1. Install dependencies
pip install -r backend/requirements.txt
2. Start the backend
cd backend
python -m uvicorn main:app --reload

The API will run at:

http://127.0.0.1:8000
3. Start the frontend

Open frontend/index.html using a local web server such as VS Code Live Server.

Example:

http://127.0.0.1:5500
Disclaimer

WebSec Auditor is an educational and defensive security auditing tool designed to identify common web security configuration issues. It does not perform exploitation or penetration testing.

Author

Tala Ammar