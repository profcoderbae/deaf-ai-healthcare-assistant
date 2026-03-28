# Deaf AI Healthcare Assistant

> AI-powered healthcare communication system for deaf patients using sign language detection, avatar-based interaction, and real-time translation.

Built for hackathon submission - fully functional prototype using open-source tools.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEAF AI HEALTHCARE ASSISTANT                      │
├──────────────────────────────┬──────────────────────────────────────┤
│   PART 1: KIOSK / CHATBOT   │   PART 2: REAL-TIME TRANSLATOR      │
│                              │                                      │
│  [Webcam] → Wave Detection   │  [Staff Receives Patient]           │
│       ↓                      │       ↓                              │
│  [Avatar "Thandi" Greets]    │  [Start Translation Mode]           │
│       ↓                      │       ↓                              │
│  [Mode: Text or Sign]        │  [Webcam] → Sign Detection          │
│       ↓                      │       ↓          ↑                   │
│  [Triage Questions]          │  [Text + Audio] → Doctor             │
│       ↓                      │       ↓                              │
│  [Symptom Analysis]          │  Doctor Speaks → [Speech-to-Text]    │
│       ↓                      │       ↓                              │
│  [Department Matching]       │  [Avatar Signs] → Patient            │
│       ↓                      │       ↓                              │
│  [QR Code + Directions]      │  [Appointment/Prescription QR]      │
└──────────────────────────────┴──────────────────────────────────────┘

Tech Stack:
├── Backend:  Python Flask
├── AI:       Groq/OpenAI (or Demo mode - no API key needed)
├── Vision:   MediaPipe Hands (in-browser hand detection)
├── Avatar:   SVG + CSS animations
├── Speech:   Web Speech API (TTS + STT)
├── QR:       Python qrcode library
├── Database: SQLite
└── Frontend: HTML/CSS/JS + Tailwind CSS
```

---

## Quick Start

### Prerequisites
- Python 3.8+
- Modern web browser (Chrome recommended for Speech API)
- Webcam

### 1. Install Dependencies

```bash
cd "Deaf AI asistance"
pip install -r requirements.txt
```

### 2. (Optional) Set AI Provider

The app works in **Demo Mode** by default (no API key needed).

For AI-powered free-form responses, set one of:

```bash
# Option A: Groq (free, fast)
set AI_PROVIDER=groq
set GROQ_API_KEY=your_groq_api_key_here

# Option B: OpenAI
set AI_PROVIDER=openai
set OPENAI_API_KEY=your_openai_api_key_here
```

Get a free Groq API key at: https://console.groq.com/

### 3. Run the Application

```bash
python app.py
```

### 4. Open in Browser

| View | URL | Purpose |
|------|-----|---------|
| **Kiosk** (Part 1) | http://localhost:5000/ | Patient-facing chatbot |
| **Staff Dashboard** | http://localhost:5000/staff | Medical staff view |
| **Translator** (Part 2) | Opens from Staff Dashboard | Real-time translation |

---

## Demo Walkthrough

### Part 1: AI Healthcare Chatbot (Kiosk)

1. **Open** `http://localhost:5000/` on the kiosk screen
2. **Wave** at the webcam (or click "tap here to start")
3. **Enter** patient name
4. **Choose** communication mode: Text or Sign Language
5. **Answer** triage questions through Thandi (the avatar)
6. **Receive** department assignment + receipt number
7. **Scan** QR code for GPS directions (if unfamiliar with hospital)

### Part 2: Real-time Translator

1. **Staff** opens `http://localhost:5000/staff`
2. **Click** "Receive Patient" for a waiting patient
3. **Click** "Start Translation" (top right)
4. **Patient signs** → Webcam detects gestures → Text + Audio for doctor
5. **Doctor speaks** → Click microphone → Avatar signs back to patient
6. **Doctor types** appointment date → Generate QR code
7. **Doctor writes** prescription → QR sent to patient + pharmacy notified

---

## Features

### Gesture Detection
- **Wave** 👋 → Triggers greeting / starts interaction
- **Thumbs Up** 👍 → Yes / Confirm
- **Fist** ✊ → No
- **Open Palm** ✋ → Wait
- **Pointing** 👆 → Select / Next phrase
- **Peace** ✌️ → Thank you
- **OK Sign** 👌 → OK / Agree

### Avatar "Thandi"
- SVG-based healthcare avatar with medical scrubs
- Animated arms for signing simulation
- Facial expressions (happy, concerned, neutral)
- Name badge and stethoscope

### Hospital Database (Seeded)
- 12 Departments (General Practice, Emergency, Cardiology, etc.)
- 13 Medical staff members
- South African doctor/nurse names
- GPS coordinates for each department
- Keyword-based department matching

### QR Codes
- **Directions**: Google Maps walking directions to department
- **Appointments**: Date, time, department, doctor details
- **Prescriptions**: Medication, dosage, pharmacy notification

---

## Project Structure

```
Deaf AI asistance/
├── app.py                     # Flask application (all routes)
├── config.py                  # Configuration
├── database.py                # SQLite database + seed data
├── requirements.txt           # Python dependencies
├── hospital.db                # Auto-created SQLite database
│
├── services/
│   ├── __init__.py
│   ├── chatbot.py             # AI chatbot + triage flow
│   └── qr_service.py          # QR code generation
│
├── templates/
│   ├── kiosk.html             # Part 1: Patient kiosk interface
│   ├── translator.html        # Part 2: Real-time translator
│   └── staff.html             # Staff dashboard
│
└── static/
    ├── css/
    │   └── main.css           # Application styles
    └── js/
        ├── gesture.js         # MediaPipe hand gesture detection
        └── avatar.js          # SVG avatar with animations
```

---

## Technology Choices & Why

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend | Flask (Python) | Lightweight, fast to prototype |
| Hand Detection | MediaPipe Hands | Google's ML, runs in-browser, no server GPU needed |
| Avatar | SVG + CSS Animations | Lightweight, no 3D rendering needed, works everywhere |
| AI Chat | Groq/OpenAI/Demo | Flexible: free API or works offline in demo mode |
| Speech | Web Speech API | Built into Chrome, no extra dependencies |
| QR Codes | Python qrcode | Simple, reliable, generates PNG |
| Database | SQLite | Zero-config, perfect for prototype |
| Styling | Tailwind CSS (CDN) | Rapid UI development, professional look |

---

## Hospital Configuration

Edit `config.py` to customize:

```python
HOSPITAL_NAME = 'Your Hospital Name'
HOSPITAL_LAT = -33.9137    # Hospital latitude
HOSPITAL_LNG = 18.8603     # Hospital longitude
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/triage/flow` | Get triage conversation flow |
| POST | `/api/triage/complete` | Complete triage, get department |
| GET | `/api/patients/waiting` | List waiting patients |
| POST | `/api/patients/:id/receive` | Mark patient as received |
| POST | `/api/consultation/start` | Start translation session |
| POST | `/api/consultation/:id/message` | Save transcript message |
| POST | `/api/chat` | AI chat (translator mode) |
| POST | `/api/qr/appointment` | Generate appointment QR |
| POST | `/api/qr/prescription` | Generate prescription QR |
| GET | `/api/departments` | List all departments |

---

## License

Open source - built for hackathon demonstration purposes.
