from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    session,
    redirect,
    url_for,
)
from flask_cors import CORS
import json
import os
import re
from datetime import datetime, timedelta
import requests
from urllib.parse import urlparse
import hashlib
import secrets
from dotenv import load_dotenv

# Try to import Firebase Admin, but don't fail if it doesn't work
try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    FIREBASE_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import firebase_admin: {e}")
    print("Application will continue without Firebase storage")
    firebase_admin = None
    credentials = None
    firestore = None
    FIREBASE_AVAILABLE = False

# Try to import Google AI SDK, but don't fail if it doesn't work
try:
    import google.generativeai as genai

    GENAI_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import google.generativeai: {e}")
    print("Will use REST API instead")
    genai = None
    GENAI_AVAILABLE = False

app = Flask(__name__, static_folder="static", static_url_path="/static")
load_dotenv()
app.secret_key = os.environ.get(
    "SECRET_KEY", "your-secret-key-change-in-production-" + secrets.token_hex(16)
)
CORS(app, supports_credentials=True)

# Admin credentials
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = hashlib.sha256(
    os.environ.get("ADMIN_PASSWORD", "admin123").encode()
).hexdigest()

# Store active sessions (in production, use Redis or database)
admin_sessions = {}

# Google AI Studio API Key
GOOGLE_AI_API_KEY = os.environ.get("GOOGLE_AI_API_KEY", "")

# Try to initialize Gemini SDK, fallback to REST API if it fails
model = None
if GENAI_AVAILABLE:
    try:
        genai.configure(api_key=GOOGLE_AI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")
        print("Google AI SDK initialized successfully")
    except Exception as e:
        print(f"Google AI SDK initialization warning: {e}")
        print("Will use REST API instead")
        model = None
else:
    print("Using REST API for Google AI (SDK not available)")

# Firebase configuration
firebase_config = {
    "apiKey": os.environ.get("FIREBASE_API_KEY", ""),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", ""),
    "databaseURL": os.environ.get("FIREBASE_DATABASE_URL", ""),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID", ""),
    "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET", ""),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID", ""),
    "appId": os.environ.get("FIREBASE_APP_ID", ""),
}

# Firebase Realtime Database URL
FIREBASE_RTDB_URL = firebase_config["databaseURL"].rstrip("/")
FIREBASE_RTDB_API_KEY = firebase_config["apiKey"]

# Initialize Firebase (for Realtime Database, we use REST API)
print("Using Firebase Realtime Database via REST API")
db = "realtime_db"  # Marker that we're using Realtime DB

# Model initialization moved above (with error handling)


# HTML Routes
@app.route("/")
def index():
    """Serve main scanning interface"""
    return send_from_directory("templates", "index.html")


@app.route("/admin")
def admin():
    """Serve admin dashboard"""
    return send_from_directory("templates", "admin.html")


@app.route("/login")
def login():
    """Serve login page"""
    return send_from_directory("templates", "login.html")


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.json
        username = data.get("username", "")
        password = data.get("password", "")

        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Verify credentials
        if username == ADMIN_USERNAME and password_hash == ADMIN_PASSWORD_HASH:
            # Create session
            session_id = secrets.token_hex(32)
            admin_sessions[session_id] = {
                "username": username,
                "login_time": datetime.now().isoformat(),
            }

            return jsonify(
                {
                    "success": True,
                    "session_id": session_id,
                    "token": session_id,  # Also return as token for compatibility
                    "message": "Login successful",
                }
            )
        else:
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/check", methods=["GET"])
def admin_check():
    """Check if admin is authenticated"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"authenticated": False, "error": "No token provided"}), 401

        token = auth_header.replace("Bearer ", "").strip()

        # Check if session exists
        if token in admin_sessions:
            session_data = admin_sessions[token]
            # Check if session is not too old (24 hours)
            login_time = datetime.fromisoformat(session_data["login_time"])
            if datetime.now() - login_time < timedelta(hours=24):
                return jsonify(
                    {"authenticated": True, "username": session_data["username"]}
                )
            else:
                # Session expired, remove it
                del admin_sessions[token]
                return (
                    jsonify({"authenticated": False, "error": "Session expired"}),
                    401,
                )
        else:
            return jsonify({"authenticated": False, "error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"authenticated": False, "error": str(e)}), 401


@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    """Admin logout endpoint"""
    try:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "").strip()
            if token in admin_sessions:
                del admin_sessions[token]
        return jsonify({"success": True, "message": "Logged out successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def extract_text_from_url(url):
    """Extract text content from a URL"""
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        response.raise_for_status()
        # Simple text extraction (in production, use BeautifulSoup or similar)
        return response.text[:5000]  # Limit to 5000 chars
    except Exception as e:
        return f"Error fetching URL: {str(e)}"


def analyze_scam_rest_api(text_content):
    """Analyze text using Google AI REST API"""
    prompt = f"""You are an expert scam detection AI. Analyze the following text or content thoroughly and determine if it's a scam with high accuracy.

Consider these scam indicators:
- Urgent language demanding immediate action
- Requests for personal information, passwords, or financial details
- Promises of easy money, prizes, or unrealistic returns
- Threats or warnings about account closure
- Suspicious links or domains
- Poor grammar and spelling errors
- Requests for payment or money transfers
- Impersonation of legitimate companies
- Too good to be true offers
- Pressure tactics and time limits

Provide your analysis in the following EXACT JSON format (no markdown, no code blocks, just pure JSON):
{{
    "scam_percentage": <number between 0-100>,
    "is_scam": <true or false>,
    "confidence": <number between 0-100>,
    "indicators": ["indicator1", "indicator2"],
    "explanation": "detailed explanation",
    "recommendations": "what the user should do"
}}

Text to analyze:
{text_content}

Respond with ONLY valid JSON, no additional text, no markdown formatting."""

    # Try multiple model names and API versions with different auth methods
    # Format: (model_name, api_version, use_header_auth)
    models_to_try = [
        ("gemini-2.0-flash", "v1beta", True),  # Working model from user's example
        ("gemini-2.0-flash-exp", "v1beta", True),
        ("gemini-1.5-pro", "v1beta", True),
        ("gemini-1.5-flash", "v1beta", True),
        ("gemini-pro", "v1beta", True),
        ("gemini-2.0-flash", "v1", True),
        ("gemini-1.5-pro", "v1", True),
        ("gemini-1.5-flash", "v1", True),
        ("gemini-pro", "v1", True),
        # Fallback to query parameter auth
        ("gemini-2.0-flash", "v1beta", False),
        ("gemini-1.5-pro", "v1beta", False),
        ("gemini-1.5-flash", "v1beta", False),
        ("gemini-pro", "v1beta", False),
    ]

    for model_name, api_version, use_header_auth in models_to_try:
        try:
            # Build URL
            url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent"

            # Build payload
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            # Build headers
            headers = {"Content-Type": "application/json"}

            # Add API key to header or URL
            if use_header_auth:
                headers["X-goog-api-key"] = GOOGLE_AI_API_KEY
            else:
                url = f"{url}?key={GOOGLE_AI_API_KEY}"

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()

                if "candidates" in data and len(data["candidates"]) > 0:
                    if (
                        "content" in data["candidates"][0]
                        and "parts" in data["candidates"][0]["content"]
                    ):
                        result_text = data["candidates"][0]["content"]["parts"][0][
                            "text"
                        ].strip()

                        # Clean the response (remove markdown code blocks if present)
                        if result_text.startswith("```json"):
                            result_text = result_text[7:]
                        if result_text.startswith("```"):
                            result_text = result_text[3:]
                        if result_text.endswith("```"):
                            result_text = result_text[:-3]
                        result_text = result_text.strip()

                        # Try to extract JSON if wrapped in text
                        json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
                        if json_match:
                            result_text = json_match.group(0)

                        result = json.loads(result_text)

                        # Validate and ensure scam_percentage is accurate
                        if "scam_percentage" not in result:
                            # Calculate from is_scam if needed
                            result["scam_percentage"] = (
                                85 if result.get("is_scam", False) else 15
                            )

                        # Ensure percentage is in valid range
                        result["scam_percentage"] = max(
                            0, min(100, int(result.get("scam_percentage", 50)))
                        )
                        result["is_scam"] = result.get("scam_percentage", 0) >= 50
                        result["confidence"] = max(
                            0, min(100, int(result.get("confidence", 75)))
                        )

                        print(
                            f"Successfully used model: {model_name} with {api_version}"
                        )
                        return result
                    else:
                        raise Exception("Invalid response structure")
                else:
                    raise Exception("No candidates in response")
            elif response.status_code == 404:
                # Try next model
                continue
            else:
                error_text = (
                    response.text[:500]
                    if hasattr(response, "text")
                    else str(response.status_code)
                )
                print(
                    f"API error with {model_name}/{api_version}: {response.status_code} - {error_text}"
                )
                if response.status_code not in [404, 400]:
                    response.raise_for_status()
                continue
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If we got a response but can't parse it, try next model
            if (
                "response" in locals()
                and hasattr(response, "status_code")
                and response.status_code == 200
            ):
                print(f"Parse error with {model_name}/{api_version}: {str(e)}")
                continue
            error_msg = f"Parse error: {str(e)}"
            if "response" in locals() and hasattr(response, "text"):
                error_msg += f" - Response: {response.text[:200]}"
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            # Network error, try next model
            if "404" in str(e):
                continue
            print(f"Request error with {model_name}/{api_version}: {str(e)}")
            # Don't raise on network errors, try next model
            continue

    # If all models failed
    raise Exception(
        "AI service temporarily unavailable. The system has switched to the built-in scam detection engine."
    )


def analyze_scam(text_content):
    """Analyze text for scam indicators using Google AI"""
    prompt = f"""You are an expert scam detection AI. Analyze the following text or content thoroughly and determine if it's a scam with high accuracy.

Consider these scam indicators:
- Urgent language demanding immediate action
- Requests for personal information, passwords, or financial details
- Promises of easy money, prizes, or unrealistic returns
- Threats or warnings about account closure
- Suspicious links or domains
- Poor grammar and spelling errors
- Requests for payment or money transfers
- Impersonation of legitimate companies
- Too good to be true offers
- Pressure tactics and time limits

Provide your analysis in the following EXACT JSON format (no markdown, no code blocks, just pure JSON):
{{
    "scam_percentage": <number between 0-100>,
    "is_scam": <true or false>,
    "confidence": <number between 0-100>,
    "indicators": ["indicator1", "indicator2"],
    "explanation": "detailed explanation",
    "recommendations": "what the user should do"
}}

Text to analyze:
{text_content}

Respond with ONLY valid JSON, no additional text, no markdown formatting."""

    try:
        # Try SDK first if available
        if model is not None:
            try:
                response = model.generate_content(prompt)
                result_text = response.text.strip()

                # Clean the response (remove markdown code blocks if present)
                if result_text.startswith("```json"):
                    result_text = result_text[7:]
                if result_text.startswith("```"):
                    result_text = result_text[3:]
                if result_text.endswith("```"):
                    result_text = result_text[:-3]
                result_text = result_text.strip()

                # Try to extract JSON if wrapped in text
                json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group(0)

                result = json.loads(result_text)

                # Validate and ensure scam_percentage is accurate
                if "scam_percentage" not in result:
                    result["scam_percentage"] = (
                        85 if result.get("is_scam", False) else 15
                    )

                result["scam_percentage"] = max(
                    0, min(100, int(result.get("scam_percentage", 50)))
                )
                result["is_scam"] = result.get("scam_percentage", 0) >= 50
                result["confidence"] = max(
                    0, min(100, int(result.get("confidence", 75)))
                )

                return result
            except Exception as sdk_error:
                print(f"SDK error: {sdk_error}, falling back to REST API")
                return analyze_scam_rest_api(text_content)
        else:
            # Use REST API directly
            return analyze_scam_rest_api(text_content)

    except Exception as e:
        # Final fallback response if all methods fail
        error_msg = str(e)
        print(f"Scam analysis error: {error_msg}")

        # Try to provide a basic analysis based on common scam keywords
        text_lower = text_content.lower()
        scam_keywords = [
            "urgent",
            "verify",
            "suspended",
            "click here",
            "limited time",
            "free money",
            "congratulations",
            "winner",
            "prize",
            "claim now",
            "act now",
            "expires",
            "account closed",
            "verify account",
            "update payment",
            "confirm identity",
        ]

        keyword_matches = [kw for kw in scam_keywords if kw in text_lower]
        basic_percentage = min(90, len(keyword_matches) * 15)

        return {
            "scam_percentage": basic_percentage if keyword_matches else 30,
            "is_scam": basic_percentage >= 50,
            "confidence": 40,
            "indicators": (
                keyword_matches
                if keyword_matches
                else ["Unable to perform full AI analysis"]
            ),
            "explanation": (
                "AI service temporarily unavailable. "
                "The system has switched to the built-in scam detection engine. "
                f"Found {len(keyword_matches)} potential scam indicators."
            ),
            "recommendations": "Be cautious. Verify the source independently. Do not provide personal information or click suspicious links.",
        }


@app.route("/api/scan", methods=["POST"])
def scan_content():
    """Scan text or URL for scam indicators"""
    try:
        data = request.json
        content_type = data.get("type", "text")  # 'text' or 'url'
        content = data.get("content", "")

        if not content:
            return jsonify({"error": "No content provided"}), 400

        # Extract text from URL if needed
        if content_type == "url":
            text_content = extract_text_from_url(content)
            original_url = content
        else:
            text_content = content
            original_url = None

        # Analyze with AI
        analysis = analyze_scam(text_content)

        # Store in Firebase Realtime Database
        scan_data = {
            "type": content_type,
            "content": content[:500],  # Store first 500 chars
            "url": original_url,
            "scam_percentage": analysis.get("scam_percentage", 0),
            "is_scam": analysis.get("is_scam", False),
            "confidence": analysis.get("confidence", 0),
            "indicators": analysis.get("indicators", []),
            "explanation": analysis.get("explanation", ""),
            "recommendations": analysis.get("recommendations", ""),
            "timestamp": datetime.now().isoformat(),
            "ip_address": request.remote_addr,
        }

        if db:
            try:
                # Store in Firebase Realtime Database using REST API
                scan_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
                url = f"{FIREBASE_RTDB_URL}/scans/{scan_id}.json?auth={FIREBASE_RTDB_API_KEY}"

                # Try with auth first, fallback to public write if rules allow
                response = requests.put(url, json=scan_data, timeout=5)
                if response.status_code not in [200, 201]:
                    # Try without auth (if public write is enabled)
                    url_no_auth = f"{FIREBASE_RTDB_URL}/scans/{scan_id}.json"
                    response = requests.put(url_no_auth, json=scan_data, timeout=5)

                if response.status_code in [200, 201]:
                    print(f"✓ Scan stored in Firebase Realtime Database: {scan_id}")
                else:
                    print(
                        f"Firebase storage warning: {response.status_code} - {response.text[:100]}"
                    )
            except Exception as e:
                print(f"Firebase storage error: {e}")

        return jsonify(
            {"success": True, "analysis": analysis, "timestamp": scan_data["timestamp"]}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get statistics for admin dashboard"""
    try:
        if not db:
            return jsonify(
                {
                    "total_scans": 0,
                    "scam_count": 0,
                    "safe_count": 0,
                    "average_scam_percentage": 0,
                    "recent_scans": [],
                }
            )

        # Fetch from Firebase Realtime Database
        url = f"{FIREBASE_RTDB_URL}/scans.json"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return jsonify(
                {
                    "total_scans": 0,
                    "scam_count": 0,
                    "safe_count": 0,
                    "average_scam_percentage": 0,
                    "recent_scans": [],
                }
            )

        data = response.json()
        if not data:
            return jsonify(
                {
                    "total_scans": 0,
                    "scam_count": 0,
                    "safe_count": 0,
                 "average_scam_percentage": 0,
                    "recent_scans": [],
                }
            )

        # Convert to list and process
        all_scans = []
        for scan_id, scan_data in data.items():
            scan_data["id"] = scan_id
            all_scans.append(scan_data)

        # Sort by timestamp
        all_scans.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        total_scans = len(all_scans)
        scam_count = 0
        safe_count = 0
        total_percentage = 0
        recent_scans = []

        for scan_data in all_scans:
            total_percentage += scan_data.get("scam_percentage", 0)

            if scan_data.get("is_scam", False):
                scam_count += 1
            else:
                safe_count += 1

            # Get recent scans (last 10)
            if len(recent_scans) < 10:
                recent_scans.append(
                    {
                        "id": scan_data.get("id", ""),
                        "type": scan_data.get("type", "text"),
                        "scam_percentage": scan_data.get("scam_percentage", 0),
                        "is_scam": scan_data.get("is_scam", False),
                        "timestamp": scan_data.get("timestamp", ""),
                        "content_preview": scan_data.get("content", "")[:100],
                    }
                )

        # Calculate average
        average_percentage = total_percentage / total_scans if total_scans > 0 else 0

        return jsonify(
            {
                "total_scans": total_scans,
                "scam_count": scam_count,
                "safe_count": safe_count,
                "average_scam_percentage": round(average_percentage, 2),
                "recent_scans": recent_scans,
            }
        )

    except Exception as e:
        print(f"Error in get_stats: {str(e)}")
        return (
            jsonify(
                {
                    "total_scans": 0,
                    "scam_count": 0,
                    "safe_count": 0,
                    "average_scam_percentage": 0,
                    "recent_scans": [],
                    "error": str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    print("Starting AI Scam Detector Flask App...")
    print(f"API Key available: {'Yes' if GOOGLE_AI_API_KEY else 'No'}")
    print(f"Firebase available: {FIREBASE_AVAILABLE}")
    print(f"Google AI SDK available: {GENAI_AVAILABLE}")
    print("\nAccess the app at:")
    print("  Main App: http://localhost:5000")
    print("  Admin Dashboard: http://localhost:5000/admin")
    print("  Database Viewer: http://localhost:5000/database")
    print("\nAdmin Credentials:")
    print(f"  Username: {ADMIN_USERNAME}")
    print("  Password: Check your .env file")
    print("\nPress CTRL+C to stop the server")

    app.run(host="0.0.0.0", port=5000, debug=True)
