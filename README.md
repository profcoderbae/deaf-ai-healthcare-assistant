# Deaf AI Healthcare Assistant

> **AI-powered healthcare communication system** for deaf patients at Tygerberg Hospital, using real-time sign language detection, an animated avatar assistant, and bidirectional translation between sign language and speech.

**Live Demo**: [https://deaf-ai-healthcare-assistant.onrender.com](https://deaf-ai-healthcare-assistant.onrender.com)  
**GitHub**: [profcoderbae/deaf-ai-healthcare-assistant](https://github.com/profcoderbae/deaf-ai-healthcare-assistant)

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Our Solution](#our-solution)
3. [System Architecture](#system-architecture)
4. [How It Works — Step by Step](#how-it-works--step-by-step)
5. [Sign Language Gestures Supported](#sign-language-gestures-supported)
6. [AI & Machine Learning](#ai--machine-learning)
7. [Quick Start (Run Locally)](#quick-start-run-locally)
8. [Presentation Demo Script](#presentation-demo-script)
9. [Technology Stack](#technology-stack)
10. [Project Structure](#project-structure)
11. [API Reference](#api-reference)
12. [Deployment](#deployment)
13. [Training Manual](#training-manual)
14. [Team & License](#team--license)

---

## Problem Statement

**Deaf patients face critical communication barriers in hospitals.** At Tygerberg Hospital:

- Deaf patients cannot explain symptoms to reception staff
- Doctors cannot communicate diagnoses or treatment plans effectively
- Sign language interpreters are scarce and expensive
- Miscommunication leads to misdiagnosis, delayed treatment, and poor patient outcomes
- Deaf patients often leave feeling confused, frustrated, and unheard

**This is a healthcare equity issue** — every patient deserves to be understood.

---

## Our Solution

A **two-part AI system** that enables seamless communication between deaf patients and hospital staff:

### Part 1: AI Kiosk Chatbot ("Thandi")
A self-service kiosk where deaf patients check in **using sign language or text**. An animated avatar named Thandi guides them through triage questions, identifies their symptoms, assigns the correct department, and provides QR-coded directions.

### Part 2: Real-Time Sign Language Translator
During consultations, the system translates:
- **Patient → Doctor**: Patient signs → Camera detects gestures → AI translates to text → Text is read aloud to doctor
- **Doctor → Patient**: Doctor speaks → Speech-to-text → Animated avatar signs back to patient with emoji representations

### Key Innovation
- **No interpreter needed** — the AI handles both directions of translation in real-time
- **Works in-browser** — no app installation, uses any standard webcam
- **AI sentence cleanup** — converts fragmented sign words ("pain head bad" → "I have a bad headache") using Groq AI
- **South African Sign Language (SASL)** — gestures mapped to SASL standards, not just ASL

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      DEAF AI HEALTHCARE ASSISTANT                       │
├───────────────────────────────┬─────────────────────────────────────────┤
│    PART 1: KIOSK CHATBOT     │    PART 2: REAL-TIME TRANSLATOR         │
│                               │                                         │
│  Patient waves at camera      │  Staff receives patient from dashboard  │
│         ↓                     │         ↓                               │
│  Avatar "Thandi" greets       │  Opens translator page                  │
│         ↓                     │         ↓                               │
│  Choose: Text or Sign         │  ┌──────────────────────────────────┐  │
│         ↓                     │  │  PATIENT → DOCTOR                │  │
│  Triage questions             │  │  Camera → MediaPipe Hands        │  │
│  (answer via tap or gesture)  │  │  → Server Sign Detection (ML)    │  │
│         ↓                     │  │  → Word → AI Sentence Cleanup    │  │
│  AI symptom analysis          │  │  → Text + Audio (TTS) to Doctor  │  │
│         ↓                     │  ├──────────────────────────────────┤  │
│  Department assignment        │  │  DOCTOR → PATIENT                │  │
│         ↓                     │  │  Doctor speaks → Microphone      │  │
│  Receipt number issued        │  │  → Speech-to-Text (Web API)      │  │
│         ↓                     │  │  → Animated Avatar Signs         │  │
│  QR code for GPS directions   │  │  → Emoji word-by-word display    │  │
│                               │  └──────────────────────────────────┘  │
│                               │         ↓                               │
│                               │  QR: Appointment / Prescription         │
└───────────────────────────────┴─────────────────────────────────────────┘

                        ┌───────────────────────┐
                        │    TECHNOLOGY STACK    │
                        ├───────────────────────┤
                        │ Backend:  Flask + SocketIO   │
                        │ AI Chat:  Groq (Llama 3.1)   │
                        │ Vision:   MediaPipe Tasks API │
                        │ ML:       GestureRecognizer   │
                        │           + HandLandmarker    │
                        │ Avatar:   SVG + CSS Animations│
                        │ Speech:   Web Speech API      │
                        │ QR:       Python qrcode       │
                        │ Database: SQLite              │
                        │ Frontend: Tailwind CSS        │
                        │ Deploy:   Render.com (Docker) │
                        └───────────────────────┘
```

---

## How It Works — Step by Step

### Part 1: Patient Check-In (Kiosk)

| Step | What Happens | How It Works |
|------|-------------|--------------|
| **1. Wave Hello** | Patient waves at camera to start | MediaPipe Hands detects open palm + side-to-side motion. Gesture confirmed after 2 consecutive detections. Also accepts held open palm as "Hello" |
| **2. Enter Name** | Patient types their name | Simple text input with on-screen keyboard |
| **3. Choose Mode** | Text communication or Sign Language | If Sign is chosen, webcam streams to server-side ML sign detection via WebSocket |
| **4. Triage Questions** | Thandi asks what's wrong | Multi-step conversation flow: greeting → symptoms → pain location → pain level → duration → allergies → medication → directions |
| **5. Sign-Based Answers** | Patient can answer with gestures | **Thumbs up** = Yes, **Fist** = No, **Pinch** = Pain, **Horns** = Help/Emergency. AI maps gestures to the currently displayed options |
| **6. Department Match** | AI analyzes symptoms | Keyword-based matching against 12 departments. AI provides triage summary via Groq |
| **7. Receipt & QR** | Patient gets receipt number + QR code | QR code links to Google Maps walking directions from hospital entrance to assigned department |

### Part 2: Doctor-Patient Translation

| Step | What Happens | How It Works |
|------|-------------|--------------|
| **1. Receive Patient** | Doctor clicks "Receive" on staff dashboard | Patient status changes from "waiting" to "in_consultation" |
| **2. Open Translator** | Auto-redirects to translation page | WebSocket connection established for real-time sign detection |
| **3. Patient Signs** | Camera captures hand gestures | Frames sent to server every 150ms. MediaPipe ML GestureRecognizer classifies gestures (Open_Palm, Closed_Fist, Thumb_Up, Victory, etc.). Geometric classifier handles additional SASL signs |
| **4. Words Build Up** | Detected words appear in sentence builder | 3-layer deduplication prevents repeats. Words auto-send after 5 seconds or manual send |
| **5. AI Cleanup** | Raw sign words → proper English sentence | Groq AI converts "pain head bad yesterday" → "I have had a bad headache since yesterday" |
| **6. Auto-Read Aloud** | Text-to-Speech reads patient message to doctor | Uses Web Speech API (en-ZA accent). Doctor hears what patient signed. Toggle on/off available |
| **7. Doctor Responds** | Doctor speaks or types message | Speech-to-text captures doctor's words. Auto-restarts on silence |
| **8. Avatar Signs Back** | Animated avatar displays signs to patient | Word-by-word emoji display with sign language representations. Progress bar shows signing progress |
| **9. Quick Phrases** | Doctor can tap common medical phrases | Department-specific phrase boards (Cardiology, Pulmonology, etc.) |
| **10. QR Outputs** | Appointment booking + prescription QR | Patient scans QR with phone for appointment details or prescription info |

---

## Sign Language Gestures Supported

### ML-Detected Gestures (Google GestureRecognizer — High Accuracy)

| Gesture | Visual | Meaning | Detection Method |
|---------|--------|---------|-----------------|
| Open Palm | ✋ | Hello / Wait | ML GestureRecognizer |
| Closed Fist | ✊ | No | ML GestureRecognizer |
| Thumbs Up | 👍 | Yes | ML GestureRecognizer |
| Thumbs Down | 👎 | Feeling Bad | ML GestureRecognizer |
| Victory / Peace | ✌️ | Thank You | ML GestureRecognizer |
| I Love You | 🤟 | I Love You | ML GestureRecognizer |
| Pointing Up | ☝️ | There / Look | ML GestureRecognizer |

### Geometric Gestures (Custom SASL Classifier)

| Gesture | Visual | Meaning | How to Form |
|---------|--------|---------|-------------|
| OK Sign | 👌 | OK / Agree | Thumb + index tips touching, other fingers extended |
| Horns | 🤘 | Help | Index + pinky extended, others curled |
| Call Me | 🤙 | Call | Thumb + pinky extended, others curled |
| Pinch | 🤏 | Pain | Thumb + index close together, others curled |
| Three Up | 3️⃣ | Medicine | Index + middle + ring extended |
| Flat Down | 🖐️ | Please Wait | Palm facing down, all fingers out |
| Wave | 👋 | Hello/Goodbye | Open hand moving side to side |

### Fingerspelling (A-Z) & Numbers (0-9)
All 26 ASL/SASL letters and 10 numbers are supported via geometric landmark analysis.

---

## AI & Machine Learning

### Dual Detection Pipeline
```
Camera Frame (JPEG)
       ↓
┌──────────────────┐
│ ML GestureRecognizer │ ← Google's pre-trained model (float16)
│ (7 gesture classes)  │   Open_Palm, Closed_Fist, Thumb_Up, 
│                      │   Thumb_Down, Victory, ILoveYou, Pointing_Up
└──────┬───────────────┘
       ↓ if ML confidence < 0.7
┌──────────────────┐
│ HandLandmarker       │ ← 21 hand landmarks extracted
│ → Geometric Rules    │   Finger states + distances + angles
│ (15+ gesture classes)│   OK, Horns, Pinch, Letters A-Z, Numbers 0-9
└──────┬───────────────┘
       ↓
┌──────────────────┐
│ Motion Detection     │ ← Frame buffer (30 frames)
│ Wave, Nod, Shake     │   Wrist position tracking over time
└──────┬───────────────┘
       ↓
Word Output → Sentence Builder → AI Cleanup (Groq Llama 3.1)
```

### AI Sentence Cleanup (Groq)
- **Model**: `llama-3.1-8b-instant` via Groq Cloud (free tier)
- **Purpose**: Converts raw sign language words into grammatically correct English
- **Example**: `"pain stomach bad two day"` → `"I have had bad stomach pain for two days"`
- **Fallback**: If Groq is unavailable, raw words are sent as-is

### Word Deduplication (3-Layer)
1. **Consecutive block**: Same word detected back-to-back is ignored
2. **Time window**: Same word within 5 seconds is ignored
3. **Per-sentence**: Each word appears only once per sentence

---

## Quick Start (Run Locally)

### Prerequisites
- **Python 3.8+** (tested on 3.11, 3.13)
- **Chrome browser** (best support for Speech API + MediaPipe)
- **Webcam** (for sign language detection)

### Step 1: Clone the Repository

```bash
git clone https://github.com/profcoderbae/deaf-ai-healthcare-assistant.git
cd deaf-ai-healthcare-assistant
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up AI Provider (Optional)

The app works in **Demo Mode** by default (no API key needed). For full AI features:

**Windows (PowerShell):**
```powershell
$env:AI_PROVIDER = "groq"
$env:GROQ_API_KEY = "your_groq_api_key_here"
```

**Linux/Mac:**
```bash
export AI_PROVIDER=groq
export GROQ_API_KEY=your_groq_api_key_here
```

Or create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at: https://console.groq.com/

### Step 4: Run the Application

```bash
python app.py
```

### Step 5: Open in Browser

| Page | URL | Who Uses It |
|------|-----|-------------|
| 🏥 **Kiosk** (Part 1) | http://localhost:5000/ | Patient self-check-in |
| 👨‍⚕️ **Staff Dashboard** | http://localhost:5000/staff | Doctors & nurses |
| 🔄 **Translator** (Part 2) | Opens from Staff Dashboard | Doctor + patient during consultation |
| 📖 **Training Manual** | http://localhost:5000/training | Staff training & gesture reference |

---

## Presentation Demo Script

> **Use this script to demonstrate the system in a live presentation.** Open two browser tabs side-by-side: one for the Kiosk and one for the Staff Dashboard.

### Setup (Before Presentation)
1. Run `python app.py` in terminal
2. Open **Tab 1**: `http://localhost:5000/` (Kiosk — full screen)
3. Open **Tab 2**: `http://localhost:5000/staff` (Staff Dashboard)
4. Make sure webcam is available and allowed

---

### Act 1: Patient Arrives (Kiosk Tab — 2 minutes)

**Narration**: *"A deaf patient arrives at Tygerberg Hospital. Instead of struggling to communicate at reception, they approach our AI kiosk."*

1. **Show the kiosk screen** — Thandi's wave prompt is visible
2. **Wave your hand** at the camera — the system detects the wave and moves to the next screen
   - *"The patient waves hello and the system recognizes the gesture using MediaPipe's ML hand detection"*
3. **Type a name** (e.g., "Sipho") and click Continue
4. **Choose "South African Sign Language"** mode
   - *"The patient chooses to communicate in sign language — no typing needed"*
5. **Show the triage flow** — Thandi asks what's wrong
   - Click **"Pain or Injury"** (or show thumbs up/fist for yes/no if prompted)
   - Select **"Head"** for pain location
   - Select **"Moderate"** pain level
   - Select **"A few days"** duration
   - Select **"No known allergies"**
   - Select **"No medication"**
   - Select **"No, I need directions"**
   - *"The AI analyzed the patient's symptoms and assigned them to the correct department"*
6. **Show the results** — Receipt number, department, assigned doctor
7. **Show the QR code** — *"The patient scans this with their phone and gets walking directions to their department inside the hospital"*

---

### Act 2: Doctor Sees Patient (Staff Tab — 3 minutes)

**Narration**: *"Now the doctor receives this patient on their dashboard."*

1. **Switch to Staff Dashboard tab**
2. **Show the patient** in the waiting list with their triage summary
3. **Click "Receive"** — opens the translator automatically
   - *"The real-time translation session begins"*

**Patient → Doctor (Sign to Speech):**

4. **Show thumbs up** to camera → "Yes" appears in the sentence builder
   - *"The patient signs 'yes' and the system translates it to text"*
5. **Show fist** → "No" appears
6. **Show pinch gesture** → "Pain" appears
7. **Point up** → "There" appears
8. Wait for auto-send (5s) or click Send
   - *"The raw sign words are sent to Groq AI which cleans them into a proper English sentence"*
   - *"The doctor HEARS the patient's message read aloud through text-to-speech — no sign language knowledge needed"*

**Doctor → Patient (Speech to Sign):**

9. **Click the microphone** button
10. **Speak**: "Where does it hurt?"
    - *"The doctor's speech is captured and converted to text"*
    - *"Our animated avatar displays the message word-by-word with sign language emoji representations so the deaf patient can understand"*
11. **Type** a message: "I will prescribe some medicine"
    - Click Send → Avatar signs the message

**QR Outputs:**

12. **Click "Book Appointment"** → Fill in date/doctor → Generate QR
    - *"The patient scans this QR to save their appointment details"*
13. **Click "Write Prescription"** → Enter medication → Generate QR
    - *"The prescription QR can be scanned at the pharmacy"*

---

### Act 3: Summary (30 seconds)

**Narration**: *"In this demonstration we showed:*
- *A deaf patient checking in using only sign language — no interpreter needed*
- *AI-powered triage that correctly identifies symptoms and assigns departments*
- *Real-time bidirectional translation between sign language and speech*
- *QR codes for directions, appointments, and prescriptions*
- *All built with open-source tools: MediaPipe, Flask, Groq AI, and Web Speech API*
- *Deployed and accessible from any device with a camera and browser"*

---

## Technology Stack

| Component | Technology | Why This Choice |
|-----------|-----------|-----------------|
| **Backend** | Flask 3.0 + Flask-SocketIO | Lightweight, real-time WebSocket support for sign detection |
| **Sign Detection (ML)** | MediaPipe GestureRecognizer | Google's pre-trained model, 7 gestures at >90% accuracy, runs server-side |
| **Sign Detection (Custom)** | MediaPipe HandLandmarker | 21 hand landmarks for geometric SASL gesture classification |
| **AI Chat** | Groq Cloud (Llama 3.1 8B) | Free tier, <500ms response time, sentence cleanup |
| **Avatar** | SVG + CSS Animations | Lightweight, works everywhere, no 3D rendering needed |
| **Speech-to-Text** | Web Speech API | Built into Chrome, zero dependencies, supports en-ZA |
| **Text-to-Speech** | Web Speech API | Built into Chrome, reads patient messages to doctor |
| **QR Codes** | Python qrcode + Pillow | Google Maps directions, appointment details, prescriptions |
| **Database** | SQLite | Zero-config, auto-seeded with 12 departments + 13 staff |
| **Frontend** | Tailwind CSS (CDN) | Rapid development, responsive, professional UI |
| **Hand Overlay** | MediaPipe Hands (browser) | Real-time hand landmark visualization on webcam feed |
| **Deployment** | Docker on Render.com | Free tier, WebSocket support, auto-deploy from GitHub |

---

## Project Structure

```
deaf-ai-healthcare-assistant/
│
├── app.py                          # Main Flask app (routes, WebSocket handlers, sign detection)
├── config.py                       # Configuration (env vars: API keys, hospital settings)
├── database.py                     # SQLite DB: departments, staff, patients, consultations
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker deployment (MediaPipe GL dependencies)
├── render.yaml                     # Render.com deployment blueprint
├── .env                            # Local environment variables (gitignored)
├── TRAINING_MANUAL.html            # Staff training guide (served at /training)
│
├── models/                         # MediaPipe ML models (auto-downloaded)
│   ├── hand_landmarker.task        # Hand landmark detection model
│   └── gesture_recognizer.task     # Google's gesture classification model
│
├── services/
│   ├── sign_detector.py            # Server-side sign detection (ML + geometric + motion)
│   ├── chatbot.py                  # AI chatbot, triage flow, sentence cleanup
│   └── qr_service.py              # QR code generation (directions, appointments, Rx)
│
├── templates/
│   ├── kiosk.html                  # Part 1: Patient kiosk with avatar Thandi
│   ├── staff.html                  # Staff dashboard (patient list, receive, complete)
│   └── translator.html             # Part 2: Real-time sign ↔ speech translator
│
└── static/
    ├── css/main.css                # Global styles, animations, webcam overlay
    └── js/
        ├── gesture.js              # Client-side MediaPipe Hands gesture detection (wave)
        ├── sign_detect.js          # SocketIO sign detection client (frames → server)
        ├── avatar.js               # SVG healthcare avatar "Thandi" with animations
        └── sign_avatar.js          # Sign language emoji display for doctor messages
```

---

## API Reference

### Patient Flow
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/triage/flow` | Get triage conversation steps |
| POST | `/api/triage/complete` | Submit triage answers, get department |
| GET | `/api/patients/all` | List all patients (all statuses) |
| GET | `/api/patients/waiting` | List waiting patients |
| POST | `/api/patients/:id/receive` | Doctor receives a patient |
| POST | `/api/patients/:id/complete` | Mark patient as done |

### Translation & AI
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/consultation/start` | Start translation session |
| POST | `/api/consultation/:id/message` | Save transcript message |
| POST | `/api/chat` | AI-powered chat response |
| POST | `/api/cleanup-sentence` | Convert raw sign words → proper English |

### QR Codes & Data
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/qr/directions` | Generate GPS directions QR |
| POST | `/api/qr/appointment` | Generate appointment QR |
| POST | `/api/qr/prescription` | Generate prescription QR |
| GET | `/api/departments` | List all 12 hospital departments |

### WebSocket Events
| Event | Direction | Purpose |
|-------|-----------|---------|
| `sign_frame` | Client → Server | Send webcam frame for sign detection |
| `detection` | Server → Client | Return detected gesture/word |
| `set_mode` | Client → Server | Switch detection mode (words/letters/numbers) |
| `mode_changed` | Server → Client | Confirm mode change |

---

## Deployment

### Render.com (Current - Free Tier)

The app is deployed at https://deaf-ai-healthcare-assistant.onrender.com using Docker.

**Environment variables needed on Render:**

| Variable | Value |
|----------|-------|
| `GROQ_API_KEY` | Your Groq API key |
| `AI_PROVIDER` | `groq` |
| `RENDER` | `true` |
| `HOSPITAL_NAME` | `Tygerberg Hospital` |

> **Note**: Free tier spins down after 15 minutes of inactivity. First load takes ~30s to wake up. Sign detection requires the Docker deployment for MediaPipe GL libraries.

### Run Locally (Best Experience)
For the full experience including sign language detection, run locally:
```bash
git clone https://github.com/profcoderbae/deaf-ai-healthcare-assistant.git
cd deaf-ai-healthcare-assistant
pip install -r requirements.txt
python app.py
```

---

## Training Manual

A comprehensive training manual for hospital staff is available at:
- **Web**: http://localhost:5000/training (when running locally)
- **PDF**: `TRAINING_MANUAL.pdf` in the project root

The manual covers:
- All supported gestures with visual guides
- Step-by-step instructions for the kiosk and translator
- Tips for communicating with deaf patients
- Department-specific quick phrases
- Troubleshooting guide

---

## Hospital Configuration

Edit `config.py` or set environment variables:

```python
HOSPITAL_NAME = 'Tygerberg Hospital'    # Display name
HOSPITAL_LAT = -33.9137                 # GPS latitude (for QR directions)
HOSPITAL_LNG = 18.8603                  # GPS longitude
AI_PROVIDER = 'groq'                    # 'groq', 'openai', or 'demo'
```

### Seeded Database
The system auto-creates `hospital.db` with:
- **12 Departments**: General Practice, Emergency, Cardiology, Orthopedics, Dermatology, Neurology, Ophthalmology, ENT, Pulmonology, Psychiatry, Pediatrics, Obstetrics & Gynecology
- **13 Staff Members**: South African doctor and nurse names with specializations
- **GPS Coordinates**: Per-department locations within the hospital campus

---

## Team & License

Built for the hackathon as a proof-of-concept for **accessible healthcare communication**.

Open source — MIT License. Built with open-source tools and models.
