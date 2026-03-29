# 🏥 Deaf AI Healthcare Assistant

> **AI-powered healthcare communication system for deaf patients** — using real-time sign language detection, an animated avatar assistant, and bidirectional doctor-patient translation.

> **Built for Tygerberg Hospital, Cape Town, South Africa**

[![Live Demo](https://img.shields.io/badge/Live-deaf--ai--healthcare--assistant.onrender.com-0D9488?style=for-the-badge)](https://deaf-ai-healthcare-assistant.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-ML-4285F4?style=flat-square&logo=google)](https://mediapipe.dev)
[![License](https://img.shields.io/badge/License-Open%20Source-green?style=flat-square)](LICENSE)

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [System Architecture](#-system-architecture)
- [Features](#-features)
- [How It Works — Step by Step](#-how-it-works--step-by-step)
- [Sign Language Gestures Supported](#-sign-language-gestures-supported)
- [AI & Machine Learning](#-ai--machine-learning)
- [Quick Start (Local Setup)](#-quick-start-local-setup)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Hospital Configuration](#-hospital-configuration)
- [Technology Stack & Justifications](#-technology-stack--justifications)
- [Training Manual](#-training-manual)
- [Team & License](#-team--license)

---

## 🎯 Problem Statement

**Deaf and hard-of-hearing patients face critical communication barriers in healthcare settings.** At hospitals like Tygerberg, patients struggle to:

- Communicate symptoms to triage nurses and doctors
- Understand medical instructions and diagnoses
- Navigate unfamiliar hospital buildings
- Receive prescriptions and appointment information

**This system bridges that gap** using AI, computer vision, and accessible design — requiring only a standard webcam and web browser.

---

## 💡 Solution Overview

The system has **two integrated parts**:

### Part 1: AI Healthcare Kiosk (Patient Self-Service)
A touchscreen/webcam kiosk where deaf patients **wave to start**, interact with an animated avatar named **Thandi**, answer triage questions using **sign language or text**, and receive a **department assignment with QR code directions**.

### Part 2: Real-Time Sign Language Translator (Doctor-Patient)
A split-screen translation interface where the **patient signs → camera detects → text + audio for doctor**, and the **doctor speaks/types → animated sign language emoji display for patient**. Full bidirectional communication.

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     DEAF AI HEALTHCARE ASSISTANT                        │
├──────────────────────────────────┬──────────────────────────────────────┤
│   PART 1: KIOSK / CHATBOT       │   PART 2: REAL-TIME TRANSLATOR      │
│                                  │                                      │
│  [Webcam] → Wave/Palm Detection  │  [Staff Dashboard] → Receive Patient│
│       ↓                          │       ↓                              │
│  [Avatar "Thandi" Greets]        │  [Split-Screen Translator Opens]    │
│       ↓                          │       ↓                              │
│  [Name Entry]                    │  ┌─── Patient Side ───┐             │
│       ↓                          │  │ Webcam → Sign Detect│             │
│  [Mode: Text or Sign Language]   │  │ → Sentence Builder  │             │
│       ↓                          │  │ → AI Cleanup        │             │
│  [Triage Questions]              │  │ → Text + TTS Audio  │→ Doctor    │
│  (Yes/No via thumbs up/fist)     │  └────────────────────┘             │
│       ↓                          │  ┌─── Doctor Side ────┐             │
│  [AI Symptom Analysis]           │  │ Microphone/Keyboard │             │
│       ↓                          │  │ → Speech-to-Text    │             │
│  [Department Matching]           │  │ → Emoji Sign Avatar │→ Patient   │
│       ↓                          │  └────────────────────┘             │
│  [Receipt # + QR Directions]     │  [Appointment QR] [Prescription QR] │
└──────────────────────────────────┴──────────────────────────────────────┘

     ┌──────────── Backend Services ────────────┐
     │  Flask + SocketIO (WebSocket)             │
     │  MediaPipe Tasks API (Hand/Gesture ML)    │
     │  Groq AI (LLaMA 3.1 - Sentence Cleanup)  │
     │  SQLite (Patients, Departments, Staff)    │
     │  QR Code Generator (Directions/Rx/Appt)   │
     └──────────────────────────────────────────┘
```

---

## ✨ Features

### 🤟 Sign Language Detection
- **15 hand gestures** recognized (open palm, thumbs up/down, fist, peace, pointing, OK, ILY, etc.)
- **ASL Fingerspelling** A–Y letter recognition
- **Number signs** 0–9
- **Motion detection** — wave (hello), nod (yes), head shake (no), circular motion (stomach pain)
- **Dual detection**: Google ML GestureRecognizer + custom geometric classifiers
- **3 detection modes**: Words, Letters, Numbers — switchable in real-time

### 🧑‍⚕️ Avatar "Thandi"
- Animated SVG healthcare avatar with medical scrubs and stethoscope
- Signing animations, waving, and facial expressions (happy, concerned, neutral)
- Guides patients through the entire triage process

### 🗣 Bidirectional Translation
- **Patient → Doctor**: Sign language → Text → Audio (TTS auto-reads patient signs aloud)
- **Doctor → Patient**: Speech/typing → Text → Animated emoji sign language display
- Auto-send after 6 seconds of sign inactivity
- Session transcript with timestamps

### 🤖 AI-Powered
- **Groq AI** (LLaMA 3.1) cleans up fragmented sign words into natural English sentences
- **Smart triage**: Symptom analysis → automatic department matching
- Works in **Demo Mode** (no API key) with rule-based fallbacks

### 📱 QR Codes
- **Directions**: Google Maps walking navigation to assigned department
- **Appointments**: Date, time, doctor, department details
- **Prescriptions**: Medication name, dosage, frequency, instructions

### 🏥 Hospital System
- 12 departments with locations, floor numbers, and GPS coordinates
- 13 seeded medical staff members (South African names)
- Patient queue management (waiting → in consultation → completed)
- Keyword-based intelligent department routing

---

## 🎬 How It Works — Step by Step

### Part 1: Patient Arrives at Kiosk

| Step | What Happens | Sign Language Option |
|------|-------------|---------------------|
| 1 | Patient approaches kiosk, camera activates | — |
| 2 | **Patient waves or shows open palm** → System detects "Hello" | 👋 Wave or ✋ Open Palm |
| 3 | Name entry screen appears | Type name |
| 4 | Choose communication mode: **Text** or **Sign Language** | — |
| 5 | Avatar Thandi asks: "What brings you to the hospital?" | — |
| 6 | Patient selects symptoms (tap buttons OR use sign gestures) | 👍 Yes / ✊ No / 🤏 Pain / 🤘 Help |
| 7 | Follow-up questions: pain level, duration, allergies, medications | 👍 Thumbs up = Yes / ✊ Fist = No |
| 8 | System matches symptoms to department | — |
| 9 | **Result screen**: Receipt number, department, doctor, QR code | Scan QR with phone |

### Part 2: Doctor Consultation with Translator

| Step | What Happens | Technology Used |
|------|-------------|-----------------|
| 1 | Staff opens dashboard → clicks "Receive Patient" | Staff Dashboard |
| 2 | Translator opens with split-screen view | WebSocket connection |
| 3 | **Patient signs** in front of webcam | MediaPipe → Flask-SocketIO |
| 4 | Signs detected → words appear as chips in sentence builder | Sentence Builder UI |
| 5 | After 6s idle, sentence auto-sends | Auto-send timer |
| 6 | AI cleans up: "Hello Pain There Help" → "Hello, I have pain there and need help" | Groq API cleanup |
| 7 | **Text appears on doctor's screen + spoken aloud automatically** | Web Speech API TTS |
| 8 | **Doctor clicks microphone and speaks** | Web Speech API STT |
| 9 | Doctor's words converted to text → displayed as animated emoji signs | Emoji Sign Avatar |
| 10 | Doctor can book appointment → QR code generated for patient | QR Generator |
| 11 | Doctor can write prescription → QR code + pharmacy notified | QR Generator |

---

## 🤟 Sign Language Gestures Supported

### Word Gestures (Medical Context)

| Gesture | Hand Shape | Detected Word | Use in Triage |
|---------|-----------|---------------|---------------|
| ✋ Open Palm | All fingers extended | **Hello** | Start interaction |
| 👍 Thumbs Up | Thumb up, fingers closed | **Yes** | Confirm / Agree |
| 👎 Thumbs Down | Thumb down, fingers closed | **Feeling bad** | Indicate discomfort |
| ✊ Fist | All fingers closed | **No** | Decline / Disagree |
| ✌️ Peace / V | Index + middle extended | **Thank you** | Express gratitude |
| 👆 Pointing | Index finger extended | **There** | Indicate location |
| 👌 OK Sign | Thumb + index circle | **OK** | Acknowledge |
| 🤟 ILY | Thumb + index + pinky | **I love you** | — |
| 🤘 Horns | Index + pinky extended | **Help** | Request assistance |
| 🤙 Call Me | Thumb + pinky extended | **Call** | Request phone call |
| 🤏 Pinch | Thumb + index pinch | **Pain** | Indicate pain |
| 3️⃣ Three Up | Index + middle + ring | **Medicine** | Request medication |
| 👆 L-Shape | Thumb + index L | **Need** | Express need |
| 🖐️ Palm Down | Flat palm facing down | **Please wait** | — |
| ✋ Four Up | Four fingers (no thumb) | **Wait** | — |

### Motion-Based Detection

| Motion | Word | How to Perform |
|--------|------|---------------|
| Side-to-side wave | **Hello** | Open hand, wave left-right |
| Vertical nod (fist) | **Yes** | Closed fist, move up-down |
| Side shake (point) | **No** | Pointed finger, shake side-to-side |
| Circular motion | **Stomach pain** | Open palm, circular over stomach |
| Upward motion | **Feeling better** | Open palm, move upward |
| Downward fist | **Pain** | Fist, push downward |
| Quick clench | **Anxious** | Repeatedly open/close hand |

### ASL Fingerspelling
Letters **A through Y** recognized via geometric hand landmark analysis. Switch to **🔤 Letters** mode in the translator.

### Number Signs
Numbers **0 through 9** recognized via finger counting. Switch to **🔢 Numbers** mode in the translator.

---

## 🤖 AI & Machine Learning

### Models Used

| Model | Source | Purpose | Size |
|-------|--------|---------|------|
| **GestureRecognizer** | Google MediaPipe (open-source) | ML gesture classification (7 gestures) | ~5 MB |
| **HandLandmarker** | Google MediaPipe (open-source) | 21-point hand landmark extraction | ~12 MB |
| **Groq LLaMA 3.1 8B** | Groq Cloud (free API) | Sign sentence cleanup & chatbot | Cloud |

### Detection Pipeline

```
Camera Frame (JPEG)
    ↓
MediaPipe HandLandmarker → 21 landmarks (x, y per joint)
    ↓
┌─────────────────────────────────────────────┐
│  1. ML GestureRecognizer (7 built-in)       │ ← Highest priority
│  2. Custom Geometric Classifier (13 more)   │ ← Landmark math
│  3. ASL Letter Classifier (A-Y)             │ ← Finger angles
│  4. Number Classifier (0-9)                 │ ← Finger counting
│  5. Motion Analyzer (wave, nod, shake)      │ ← Frame sequences
└─────────────────────────────────────────────┘
    ↓
Detected Word → Sentence Builder → AI Cleanup → Doctor sees text + hears audio
```

### AI Sentence Cleanup Example

| Raw Sign Words | AI-Cleaned Sentence |
|---------------|-------------------|
| Hello Pain There Help Medicine | "Hello, I have pain there. I need help with medicine." |
| Yes Head Pain Bad | "Yes, I have a bad headache." |
| No Medicine Feeling bad | "No medication. I'm feeling bad." |
| Thank you Doctor OK | "Thank you, doctor. OK." |

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- **Python 3.8+** (tested on 3.11 and 3.13)
- **Modern web browser** (Chrome recommended for Speech API)
- **Webcam** (built-in or USB)

### Step 1: Clone the Repository

```bash
git clone https://github.com/profcoderbae/deaf-ai-healthcare-assistant.git
cd deaf-ai-healthcare-assistant
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure AI (Optional)

The app works in **Demo Mode** by default — no API key needed. For AI-powered sentence cleanup:

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

**Or create a `.env` file:**
```
GROQ_API_KEY=your_groq_api_key_here
AI_PROVIDER=groq
```

> Get a free Groq API key at https://console.groq.com/

### Step 4: Run the Application

```bash
python app.py
```

### Step 5: Open in Browser

| Page | URL | Who Uses It |
|------|-----|-------------|
| 🏥 **Patient Kiosk** | http://localhost:5000/ | Deaf patient |
| 👨‍⚕️ **Staff Dashboard** | http://localhost:5000/staff | Doctor / Nurse |
| 🔄 **Translator** | Opens from Staff Dashboard | Doctor + Patient |
| 📖 **Training Manual** | http://localhost:5000/training | Staff training |

---

## ☁️ Deployment

### Render.com (Current)

The app is deployed on Render with Docker for MediaPipe support:

- **Live URL**: https://deaf-ai-healthcare-assistant.onrender.com
- **Runtime**: Docker (Python 3.11-slim + OpenGL libraries)
- **Auto-deploy**: Pushes to `master` branch trigger automatic deployment

Configuration files:
- `Dockerfile` — Python 3.11-slim with MediaPipe GL dependencies
- `render.yaml` — Render service blueprint
- Environment variables set in Render dashboard: `GROQ_API_KEY`, `AI_PROVIDER`, `HOSPITAL_NAME`

---

## 📁 Project Structure

```
deaf-ai-healthcare-assistant/
│
├── app.py                          # Flask application — all routes & SocketIO handlers
├── config.py                       # Environment-based configuration
├── database.py                     # SQLite schema, seed data (12 depts, 13 staff)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker config for Render deployment
├── render.yaml                     # Render.com deployment blueprint
├── .env                            # Local environment variables (gitignored)
│
├── services/
│   ├── chatbot.py                  # Triage flow (15 steps), AI chat, sentence cleanup
│   ├── sign_detector.py            # MediaPipe ML + geometric gesture detection
│   └── qr_service.py              # QR code generation (directions, Rx, appointments)
│
├── models/                         # Auto-downloaded ML models
│   ├── hand_landmarker.task        # MediaPipe hand landmark model
│   └── gesture_recognizer.task     # MediaPipe gesture classifier model
│
├── templates/
│   ├── kiosk.html                  # Part 1: Patient kiosk (wave, triage, QR)
│   ├── staff.html                  # Staff dashboard (patient queue management)
│   └── translator.html             # Part 2: Real-time bidirectional translator
│
├── static/
│   ├── css/main.css                # Application styles
│   └── js/
│       ├── gesture.js              # Client-side MediaPipe gesture detection
│       ├── sign_detect.js          # SocketIO sign detection client
│       └── avatar.js               # SVG avatar with animations
│
├── TRAINING_MANUAL.html            # Staff training guide (served at /training)
└── TRAINING_MANUAL.pdf             # Printable PDF version
```

---

## 📡 API Reference

### Triage & Patient Flow

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/triage/flow` | Get triage conversation steps |
| `POST` | `/api/triage/complete` | Submit triage answers → department assignment |
| `GET` | `/api/patients/all` | List all patients (all statuses) |
| `GET` | `/api/patients/waiting` | List waiting patients |
| `POST` | `/api/patients/:id/receive` | Staff receives patient → start consultation |
| `POST` | `/api/patients/:id/complete` | Mark patient as completed |

### Translation & Communication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/consultation/start` | Start translation session |
| `POST` | `/api/consultation/:id/message` | Save transcript message |
| `POST` | `/api/chat` | AI chat (free-form chatbot) |
| `POST` | `/api/cleanup-sentence` | AI cleanup: raw sign words → proper English |

### QR Codes & Utilities

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/qr/appointment` | Generate appointment QR code |
| `POST` | `/api/qr/prescription` | Generate prescription QR code |
| `GET` | `/api/departments` | List all 12 departments |
| `GET` | `/api/departments/:id/staff` | Get staff for a department |

### WebSocket Events (SocketIO)

| Event | Direction | Description |
|-------|-----------|-------------|
| `video_frame` | Client → Server | Send camera frame for sign detection |
| `detection` | Server → Client | Return detected gesture/letter/word |
| `set_mode` | Client → Server | Switch detection mode (glosses/alpha/num) |
| `mode_changed` | Server → Client | Confirm mode switch |

---

## 🏥 Hospital Configuration

### Departments (12 Pre-Configured)

| # | Department | Location | Keywords |
|---|-----------|----------|----------|
| 1 | General Practice | Block A, Room 101 | checkup, fever, cold, flu |
| 2 | Emergency | Block A, Ground Floor | emergency, urgent, accident |
| 3 | Cardiology | Block B, Room 201 | heart, chest, blood pressure |
| 4 | Orthopedics | Block B, Room 105 | bone, joint, muscle, fracture |
| 5 | Dermatology | Block C, Room 301 | skin, rash, itch |
| 6 | Ophthalmology | Block C, Room 202 | eye, vision |
| 7 | ENT | Block C, Room 203 | ear, nose, throat |
| 8 | Neurology | Block D, Room 401 | headache, migraine, seizure |
| 9 | Psychiatry & Mental Health | Block D, Room 105 | anxiety, depression |
| 10 | Gastroenterology | Block B, Room 302 | stomach, nausea |
| 11 | Pulmonology | Block B, Room 303 | breathing, lung, asthma |
| 12 | Pharmacy | Block A, Ground Floor | medication, prescription |

### Medical Staff (13 Seeded)

South African healthcare professionals assigned to departments:
Dr. Naledi Mokoena (GP), Dr. Sipho Nkosi (Emergency), Dr. Amahle Dlamini (Cardiology), Dr. Thabo Molefe (Orthopedics), Dr. Zanele Khumalo (Dermatology), Dr. Bongani Mthembu (Ophthalmology), Dr. Lerato Mahlangu (ENT), Dr. Nompumelelo Zuma (Neurology), Dr. Kagiso Patel (Psychiatry), Dr. Thandiwe Ngcobo (Gastroenterology), Dr. Mandla Sithole (Pulmonology), Sr. Nomsa Cele (Nurse, GP), Sr. Palesa Ndaba (Nurse, Emergency)

### Customize for Your Hospital

Edit `config.py` or set environment variables:

```python
HOSPITAL_NAME = 'Your Hospital Name'
HOSPITAL_LAT = -33.9137    # GPS latitude
HOSPITAL_LNG = 18.8603     # GPS longitude
```

---

## 🔧 Technology Stack & Justifications

| Component | Technology | Why This Choice |
|-----------|-----------|-----------------|
| **Backend** | Flask + SocketIO | Lightweight Python framework with WebSocket support for real-time sign detection |
| **Hand Detection** | MediaPipe Tasks API | Google's open-source ML — runs on CPU, no GPU needed, pre-trained models |
| **Gesture ML** | GestureRecognizer (MediaPipe) | 7 built-in gestures with high accuracy, open-source, float16 optimized |
| **Custom Gestures** | Geometric Classifiers | 13 additional medical gestures using landmark math — no training data needed |
| **AI Chat** | Groq (LLaMA 3.1 8B) | Free API, fast inference, cleans up sign word fragments into sentences |
| **Avatar** | SVG + CSS Animations | Lightweight, no 3D rendering, works on any device, accessible |
| **Speech** | Web Speech API | Built into Chrome — TTS for doctor audio, STT for doctor microphone |
| **QR Codes** | Python qrcode library | Reliable, generates PNG, works offline |
| **Database** | SQLite | Zero-config, perfect for prototype, auto-creates on first run |
| **Styling** | Tailwind CSS (CDN) | Rapid UI development, responsive, professional appearance |
| **Deployment** | Docker on Render.com | Free tier, WebSocket support, auto-deploy from GitHub |

### Why Not Other Approaches?

| Alternative | Why We Didn't Use It |
|------------|---------------------|
| TensorFlow/PyTorch custom model | Requires training data, GPU, longer dev time — MediaPipe gives us production-ready models |
| 3D avatar (Unity/Three.js) | Heavy, slow to load, not accessible — SVG is instant and works everywhere |
| Separate frontend (React) | Unnecessary complexity — Flask templates with Tailwind are sufficient |
| Cloud GPU for detection | Expensive, latency — MediaPipe runs client+server on CPU |
| External translation API | No SASL-specific APIs exist — our custom gesture mapping covers medical context |

---

## 📖 Training Manual

A comprehensive staff training guide is included:

- **Web version**: http://localhost:5000/training (or `/training` on deployed URL)
- **PDF version**: `TRAINING_MANUAL.pdf` in the project root

The manual covers:
- All supported gestures with descriptions
- Step-by-step kiosk usage
- Translator operation guide
- Department-specific quick phrases
- Troubleshooting tips

---

## 👥 Team & License

**Repository**: [github.com/profcoderbae/deaf-ai-healthcare-assistant](https://github.com/profcoderbae/deaf-ai-healthcare-assistant)

Open source — built for hackathon demonstration and real-world healthcare accessibility.

---

> *"Technology should bridge gaps, not create them. Every patient deserves to be understood."*
