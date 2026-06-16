# AI Scam Detector

A modern web application that uses Google AI (Gemini) to detect scams in text and URLs. Features a beautiful user interface and comprehensive admin dashboard.

## Features

- 🔍 **Text Analysis**: Paste any suspicious text, email, or message for analysis
- 🔗 **URL Analysis**: Analyze web pages for scam indicators
- 🤖 **AI-Powered**: Uses Google Gemini AI for real-time scam detection
- 📊 **Scam Percentage**: Get a detailed percentage score of scam probability
- 📈 **Admin Dashboard**: View analytics, reports, and all scan history
- 💾 **Firebase Integration**: All scans are stored in Firebase for analytics

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Google Gemini AI (via Google AI Studio)
- **Database**: Firebase Firestore

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Firebase Setup

The application uses Firebase Firestore. The configuration is already set in the code. For production, you may want to:

1. Download your Firebase service account key
2. Place it in the project root as `serviceAccountKey.json`
3. Update `app.py` to use the service account key:

```python
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 4. Access the Application

- **User Interface**: Open `index.html` in your browser or navigate to `http://localhost:5000` (if serving via Flask)
- **Admin Dashboard**: Open `admin.html` in your browser

## API Endpoints

### POST `/api/scan`
Scan text or URL for scam indicators.

**Request Body:**
```json
{
    "type": "text" | "url",
    "content": "text content or URL"
}
```

**Response:**
```json
{
    "success": true,
    "analysis": {
        "scam_percentage": 75,
        "is_scam": true,
        "confidence": 85,
        "indicators": ["Urgent language", "Request for personal information"],
        "explanation": "Detailed explanation...",
        "recommendations": "Recommendations..."
    },
    "timestamp": "2024-01-01T12:00:00"
}
```

### GET `/api/stats`
Get statistics for admin dashboard.

**Response:**
```json
{
    "total_scans": 100,
    "scam_count": 45,
    "safe_count": 55,
    "average_scam_percentage": 42.5,
    "recent_scans": [...]
}
```

### GET `/api/scans`
Get all scans (for admin dashboard).

**Response:**
```json
{
    "scans": [...]
}
```

## Project Structure

```
Scam_Ditector_with_AI/
├── app.py                 # Flask backend server
├── requirements.txt       # Python dependencies
├── index.html            # Main user interface
├── admin.html            # Admin dashboard
├── static/
│   ├── css/
│   │   └── style.css    # All styles
│   └── js/
│       ├── app.js       # Main application logic
│       └── admin.js     # Admin dashboard logic
└── README.md            # This file
```

## Configuration

Sensitive configuration values are loaded from environment variables. Copy `.env.example` to `.env` and update the values before running the app.

Do not commit `.env` to GitHub. The project already ignores `.env` via `.gitignore`.

Example `.env` values:
```ini
SECRET_KEY=your-secret-key-change-in-production
GOOGLE_AI_API_KEY=your-google-ai-api-key-here
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.region.firebasedatabase.app/
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
HOST=localhost
PORT=5000
```

## Features in Detail

### User Interface
- Modern, dark-themed design
- Tab-based input (Text/URL)
- Real-time AI analysis
- Animated percentage display
- Detailed scam indicators
- AI-generated explanations and recommendations

### Admin Dashboard
- Real-time statistics
- Total scans, scam count, safe count
- Average scam percentage
- Recent scans table
- Complete scan history
- Auto-refresh every 30 seconds

## Notes

- The application runs on port 5000 by default
- Make sure CORS is enabled for cross-origin requests
- Firebase may require additional setup for production use
- The AI analysis may take a few seconds depending on content length

## License

This project is open source and available for use.

