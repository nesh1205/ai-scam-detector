# AI Scam Detector

An AI-powered web application developed as a Final Year Project (FYP) for the Diploma in Software Engineering. The system detects potential scams in text messages and URLs using Google Gemini AI and a rule-based fallback engine. It provides scam probability scoring, detailed explanations, recommendations, and an administrative dashboard for monitoring analytics and scan history.

---

## Project Overview

The increasing number of online scams, phishing attempts, and fraudulent messages has created a need for intelligent systems that can help users identify potential threats. This project combines Artificial Intelligence and traditional pattern-based detection techniques to analyze suspicious content and provide users with an easy-to-understand risk assessment.

The system is designed to continue functioning even when AI services are unavailable by automatically switching to a built-in rule-based detection engine.

---

## Features

### User Features

* 🔍 Text Scam Detection

  * Analyze suspicious messages, emails, SMS, and social media messages.

* 🔗 URL Scam Detection

  * Analyze suspicious URLs and websites for potential phishing indicators.

* 🤖 AI-Powered Analysis

  * Uses Google Gemini AI for intelligent scam detection and explanations.

* 🛡️ Rule-Based Fallback Engine

  * Automatically performs scam analysis when AI services are unavailable.

* 📊 Scam Probability Scoring

  * Generates a percentage-based scam risk score.

* 💡 Recommendations

  * Provides recommendations and safety precautions for users.

* ⚡ Real-Time Analysis

  * Fast and interactive scam analysis experience.

---

### Admin Features

* 📈 Dashboard Analytics
* 📋 Complete Scan History
* 📊 Scam and Safe Scan Statistics
* 📉 Average Scam Probability Reports
* 🔄 Auto-Refreshing Dashboard
* 📅 Recent Activity Monitoring

---

## Key Features

✔ Text Scam Detection

✔ URL Scam Detection

✔ AI-Powered Threat Analysis

✔ Rule-Based Fallback Detection Engine

✔ Scam Probability Scoring

✔ Detailed Explanations and Recommendations

✔ Real-Time Analytics Dashboard

✔ Firebase Data Storage

✔ Responsive Modern User Interface

---

## System Architecture

Client (HTML/CSS/JavaScript)
↓
Flask REST API
↓
Scam Detection Engine
↓
┌────────────────────┐
│ AI Analysis Engine │
│ Google Gemini AI   │
└────────────────────┘
↓
┌────────────────────┐
│ Rule-Based Engine  │
│ Pattern Detection  │
└────────────────────┘
↓
Firebase Firestore Database

---

## Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript (ES6)

### Backend

* Python
* Flask
* Flask-CORS

### Artificial Intelligence

* Google Gemini AI
* Prompt Engineering
* Rule-Based Scam Detection Engine

### Database

* Firebase Firestore

### Development Tools

* Git
* GitHub
* VS Code
* Python Virtual Environment (venv)

---

## Project Structure

```text
AI-Scam-Detector/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── index.html
├── admin.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── app.js
│       └── admin.js
│
├── screenshots/
│   ├── home.png
│   ├── analysis.png
│   └── dashboard.png
│
└── serviceAccountKey.json (Not Included)
```

---

## Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-scam-detector.git
cd ai-scam-detector
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
GOOGLE_AI_API_KEY=your-google-ai-api-key
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com/
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
HOST=localhost
PORT=5000
```

---

### 5. Run the Application

```bash
python app.py
```

The application will run on:

```text
http://localhost:5000
```

---

## Application Access

### User Interface

```
http://localhost:5000
```

### Admin Dashboard

```
http://localhost:5000/admin
```

---

## API Endpoints

### Scan Content

**POST** `/api/scan`

Request:

```json
{
  "type": "text",
  "content": "Congratulations! You have won RM10,000. Click here to claim your prize."
}
```

Response:

```json
{
  "success": true,
  "analysis": {
    "scam_percentage": 85,
    "is_scam": true,
    "confidence": 90,
    "indicators": [
      "Urgent language",
      "Suspicious links",
      "Prize scam indicators"
    ],
    "explanation": "The message contains characteristics commonly associated with online scams.",
    "recommendations": "Avoid clicking unknown links and never share personal information."
  }
}
```

---

### Get Dashboard Statistics

**GET** `/api/stats`

---

### Get All Scan History

**GET** `/api/scans`

---

## Scam Detection Workflow

1. User enters suspicious text or URL.
2. Flask API receives the request.
3. System attempts AI analysis using Google Gemini.
4. If AI is unavailable, the Rule-Based Engine is activated.
5. Scam indicators are identified.
6. Scam probability score is calculated.
7. Recommendations and explanations are generated.
8. Scan history is stored in Firebase.
9. Results are displayed to the user and dashboard.

---

## Screenshots

### Home Page

Add screenshot:

```text
screenshots/home.png
```

### Scam Analysis Page

Add screenshot:

```text
screenshots/analysis.png
```

### Admin Dashboard

Add screenshot:

```text
screenshots/dashboard.png
```

---

## Security Features

* Environment variables for API keys and secrets
* Hidden configuration files using `.gitignore`
* Firebase authentication support
* Input validation and sanitization
* CORS configuration
* Graceful AI failure handling
* Fallback scam detection engine

---

## Future Enhancements

* Multi-language scam detection
* Email attachment scanning
* Phishing image and screenshot analysis
* Browser extension integration
* Mobile application version
* Self-hosted LLM integration
* Machine learning model training using collected scam datasets
* Real-time threat intelligence integration

---

## Academic Information

**Project Title:** AI Scam Detector

**Project Type:** Final Year Project (FYP)

**Programme:** Diploma in Software Engineering

**Project Category:** Artificial Intelligence and Cybersecurity

### Learning Outcomes

* Full-Stack Web Development
* REST API Development
* Artificial Intelligence Integration
* Firebase Database Management
* Prompt Engineering
* System Design and Architecture
* Error Handling and Fault Tolerance
* Software Security Practices

---

## License

This project is developed for educational and portfolio purposes only.

---

## Author

**Thinesh Rama**

Diploma in Software Engineering Student

GitHub: https://github.com/nesh1205

---

⭐ If you find this project interesting, feel free to fork the repository and explore the source code.


