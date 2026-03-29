from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import base64
import time
import os
import config
from database import (
    init_db, get_db, create_patient, match_department, get_waiting_patients,
    receive_patient, start_consultation, save_consultation_message,
    create_appointment, create_prescription, get_patient, get_all_departments,
    get_department_staff, get_all_patients, complete_patient
)
from services.chatbot import HealthcareChatbot
from services.qr_service import (
    generate_directions_qr, generate_appointment_qr, generate_prescription_qr
)
from services.sign_detector import SignDetector, GESTURE_TO_WORD, get_word_for_gesture

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

chatbot = HealthcareChatbot()
sign_detector = SignDetector()

# Initialize database on startup
init_db()


# ─── Page Routes ───────────────────────────────────────────────────────────────

@app.route('/')
def kiosk():
    """Part 1: Healthcare Kiosk - Chatbot for deaf patients."""
    return render_template('kiosk.html', hospital_name=config.HOSPITAL_NAME)


@app.route('/translator/<int:patient_id>')
def translator(patient_id):
    """Part 2: Real-time sign language translator."""
    patient = get_patient(patient_id)
    if not patient:
        return "Patient not found", 404
    return render_template('translator.html', patient=patient, hospital_name=config.HOSPITAL_NAME)


@app.route('/staff')
def staff_dashboard():
    """Staff dashboard for receiving patients."""
    return render_template('staff.html', hospital_name=config.HOSPITAL_NAME)

@app.route('/training')
def training_manual():
    """Sign language communication training manual."""
    from flask import send_from_directory
    return send_from_directory(app.root_path, 'TRAINING_MANUAL.html')


# ─── Triage API ────────────────────────────────────────────────────────────────

@app.route('/api/triage/flow', methods=['GET'])
def get_triage_flow():
    """Get the triage conversation flow."""
    return jsonify({"flow": chatbot.get_triage_flow()})


@app.route('/api/triage/step/<step_id>', methods=['GET'])
def get_triage_step(step_id):
    """Get a specific triage step."""
    step = chatbot.get_step(step_id)
    if step:
        return jsonify(step)
    return jsonify({"error": "Step not found"}), 404


@app.route('/api/triage/complete', methods=['POST'])
def complete_triage():
    """Complete triage and assign department."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    patient_name = data.get('name', 'Patient')
    answers = data.get('answers', [])
    comm_pref = data.get('communication_preference', 'sign')
    needs_directions = data.get('needs_directions', True)

    # Analyze symptoms to find keywords
    symptom_keywords = chatbot.analyze_symptoms(answers)

    # Match to department
    department = match_department(symptom_keywords)

    # Build triage summary
    summary_parts = [a.get('label', a.get('value', '')) for a in answers]
    triage_summary = ' | '.join(summary_parts)

    # Create patient record
    patient = create_patient(
        name=patient_name,
        department_id=department['id'],
        triage_summary=triage_summary,
        triage_answers=answers,
        communication_pref=comm_pref
    )

    result = {
        "patient": patient,
        "department": department,
        "triage_summary": triage_summary,
    }

    # Generate directions QR if needed
    if needs_directions:
        qr_data = generate_directions_qr(department)
        result["qr_directions"] = qr_data

    return jsonify(result)


# ─── Patient API ───────────────────────────────────────────────────────────────

@app.route('/api/patients/waiting', methods=['GET'])
def api_waiting_patients():
    """Get all waiting patients."""
    patients = get_waiting_patients()
    return jsonify({"patients": patients})


@app.route('/api/patients/all', methods=['GET'])
def api_all_patients():
    """Get all patients grouped by status."""
    patients = get_all_patients()
    grouped = {
        'waiting': [p for p in patients if p['status'] == 'waiting'],
        'in_consultation': [p for p in patients if p['status'] == 'in_consultation'],
        'completed': [p for p in patients if p['status'] == 'completed'],
    }
    return jsonify({"patients": patients, "grouped": grouped})


@app.route('/api/patients/<int:patient_id>/complete', methods=['POST'])
def api_complete_patient(patient_id):
    """Mark patient as completed."""
    complete_patient(patient_id)
    return jsonify({"message": "Patient marked as completed"})


@app.route('/api/patients/<int:patient_id>', methods=['GET'])
def api_get_patient(patient_id):
    """Get patient details."""
    patient = get_patient(patient_id)
    if patient:
        return jsonify(patient)
    return jsonify({"error": "Patient not found"}), 404


@app.route('/api/patients/<int:patient_id>/receive', methods=['POST'])
def api_receive_patient(patient_id):
    """Mark patient as received by medical staff."""
    data = request.get_json() or {}
    staff_id = data.get('staff_id')
    patient = receive_patient(patient_id, staff_id)
    if patient:
        return jsonify({"patient": patient, "message": "Patient received successfully"})
    return jsonify({"error": "Patient not found"}), 404


# ─── Consultation API ──────────────────────────────────────────────────────────

@app.route('/api/consultation/start', methods=['POST'])
def api_start_consultation():
    """Start a new consultation session."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    patient_id = data.get('patient_id')
    staff_id = data.get('staff_id', 1)
    consultation_id = start_consultation(patient_id, staff_id)
    return jsonify({"consultation_id": consultation_id})


@app.route('/api/consultation/<int:consultation_id>/message', methods=['POST'])
def api_save_message(consultation_id):
    """Save a message to consultation transcript."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    save_consultation_message(consultation_id, data.get('sender', 'unknown'), data.get('message', ''))
    return jsonify({"status": "saved"})


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """AI chat endpoint for translator mode."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    message = data.get('message', '')
    history = data.get('history', [])
    response = chatbot.get_ai_response(message, history)
    return jsonify({"response": response})


@app.route('/api/cleanup-sentence', methods=['POST'])
def api_cleanup_sentence():
    """Clean up raw sign language words into a proper sentence using AI."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    raw = data.get('raw', '')
    if not raw or not raw.strip():
        return jsonify({"cleaned": raw})
    cleaned = chatbot.cleanup_sign_sentence(raw)
    return jsonify({"cleaned": cleaned})


# ─── QR Code API ───────────────────────────────────────────────────────────────

@app.route('/api/qr/appointment', methods=['POST'])
def api_appointment_qr():
    """Generate appointment QR code."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    patient = get_patient(data.get('patient_id'))
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    # Create appointment record
    apt = create_appointment(
        patient_id=patient['id'],
        department_id=patient.get('department_id', 1),
        staff_id=patient.get('staff_id', 1),
        date=data.get('date', ''),
        time=data.get('time', ''),
        notes=data.get('notes', '')
    )

    qr = generate_appointment_qr(
        patient_name=patient['name'],
        receipt_number=patient['receipt_number'],
        appointment_date=data.get('date', ''),
        appointment_time=data.get('time', ''),
        department_name=patient.get('department_name', ''),
        doctor_name=patient.get('staff_name', ''),
        notes=data.get('notes', '')
    )

    return jsonify(qr)


@app.route('/api/qr/prescription', methods=['POST'])
def api_prescription_qr():
    """Generate prescription QR code and notify pharmacy."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    patient = get_patient(data.get('patient_id'))
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    consultation_id = data.get('consultation_id')

    # Create prescription record
    rx_id = create_prescription(
        patient_id=patient['id'],
        consultation_id=consultation_id,
        medication=data.get('medication', ''),
        dosage=data.get('dosage', ''),
        instructions=data.get('instructions', '')
    )

    qr = generate_prescription_qr(
        patient_name=patient['name'],
        receipt_number=patient['receipt_number'],
        medication=data.get('medication', ''),
        dosage=data.get('dosage', ''),
        instructions=data.get('instructions', ''),
        doctor_name=patient.get('staff_name', '')
    )

    # In production, this would send SMS/email to pharmacy
    qr['pharmacy_notified'] = True
    qr['prescription_id'] = rx_id

    return jsonify(qr)


# ─── Department API ────────────────────────────────────────────────────────────

@app.route('/api/departments', methods=['GET'])
def api_departments():
    """Get all departments."""
    return jsonify({"departments": get_all_departments()})


@app.route('/api/departments/<int:dept_id>/staff', methods=['GET'])
def api_department_staff(dept_id):
    """Get staff in a department."""
    return jsonify({"staff": get_department_staff(dept_id)})


# ─── WebSocket Sign Detection (adapted from Hands-Up architecture) ─────────

# Per-client state for sign detection
_client_state = {}

@socketio.on('connect')
def handle_connect():
    _client_state[request.sid] = {
        'mode': 'alpha',       # 'alpha', 'num', 'glosses'
        'frame_buffer': [],    # frames for word-level detection
        'last_letter': None,
        'last_letter_count': 0,
        'last_prediction_time': 0,
        'last_word': None,     # dedup: suppress same consecutive word
        'last_gesture': None,  # dedup: track gesture name to require change
        'gesture_hold_count': 0,  # consecutive frames with same gesture
        'word_history': [],    # list of (word, timestamp) for history-based dedup
        'hand_absent_since': None,  # track when hand disappeared
        'department': None,    # department context for medical signs
        'collecting': False,
    }
    emit('status', {'msg': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    _client_state.pop(request.sid, None)

@socketio.on('set_mode')
def handle_set_mode(data):
    """Switch detection mode: alpha, num, glosses"""
    sid = request.sid
    if sid in _client_state:
        _client_state[sid]['mode'] = data.get('mode', 'alpha')
        _client_state[sid]['frame_buffer'] = []
        _client_state[sid]['last_letter'] = None
        _client_state[sid]['last_letter_count'] = 0
        _client_state[sid]['last_gesture'] = None
        _client_state[sid]['last_word'] = None
        _client_state[sid]['gesture_hold_count'] = 0
        _client_state[sid]['word_history'] = []
        if 'department' in data:
            _client_state[sid]['department'] = data['department']
        emit('mode_changed', {'mode': _client_state[sid]['mode']})

@socketio.on('set_department')
def handle_set_department(data):
    """Set department context for medical sign recognition."""
    sid = request.sid
    if sid in _client_state:
        _client_state[sid]['department'] = data.get('department')
        emit('department_set', {'department': _client_state[sid]['department']})

@socketio.on('frame')
def handle_frame(data):
    """
    Receive a camera frame (base64 JPEG) and detect sign.
    Uses ML GestureRecognizer (primary) + geometric classifier (fallback).
    Strict dedup: same word NEVER emitted twice consecutively — requires
    a different gesture or hand disappearing before re-emitting.
    """
    sid = request.sid
    state = _client_state.get(sid)
    if not state:
        return

    try:
        # Decode base64 image
        img_data = data.get('image', '')
        if ',' in img_data:
            img_data = img_data.split(',')[1]
        image_bytes = base64.b64decode(img_data)
    except Exception:
        emit('detection', {'error': 'Invalid frame data'})
        return

    # Extract landmarks
    landmarks = sign_detector.process_frame(image_bytes)
    if landmarks is None:
        # No hand visible — reset last_gesture so same word CAN be re-detected
        # after the user puts their hand down and brings it back
        state['last_gesture'] = None
        state['hand_absent_since'] = state.get('hand_absent_since') or time.time()
        emit('detection', {'status': 'no_hand'})
        return

    # Hand is present — clear absence timer
    state['hand_absent_since'] = None

    mode = state['mode']
    now = time.time()

    if mode == 'alpha':
        letter, conf = sign_detector.detect_letter(landmarks)
        if letter and conf >= 0.60:
            # Require 2 consecutive same-letter detections
            if letter == state['last_letter']:
                state['last_letter_count'] += 1
            else:
                state['last_letter'] = letter
                state['last_letter_count'] = 1

            if state['last_letter_count'] >= 2 and (now - state['last_prediction_time']) > 0.8:
                state['last_prediction_time'] = now
                state['last_letter_count'] = 0
                emit('detection', {
                    'type': 'letter',
                    'letter': letter,
                    'confidence': round(conf, 3),
                })
            else:
                emit('detection', {'status': 'collecting', 'hint': letter})
        else:
            state['last_letter'] = None
            state['last_letter_count'] = 0
            emit('detection', {'status': 'scanning'})

    elif mode == 'num':
        number, conf = sign_detector.detect_number(landmarks)
        if number and conf >= 0.60:
            if number == state.get('last_number'):
                state['last_number_count'] = state.get('last_number_count', 0) + 1
            else:
                state['last_number'] = number
                state['last_number_count'] = 1

            if state.get('last_number_count', 0) >= 2 and (now - state['last_prediction_time']) > 0.8:
                state['last_prediction_time'] = now
                state['last_number_count'] = 0
                emit('detection', {
                    'type': 'number',
                    'number': number,
                    'confidence': round(conf, 3),
                })
            else:
                emit('detection', {'status': 'collecting', 'hint': number})
        else:
            state['last_number'] = None
            state['last_number_count'] = 0
            emit('detection', {'status': 'scanning'})

    elif mode == 'glosses':
        # === 1. Try ML GestureRecognizer FIRST (Google's pre-trained model) ===
        ml_gesture, ml_conf = sign_detector.detect_ml_gesture(image_bytes)

        # === 2. Try custom geometric classifier for extra medical gestures ===
        geo_gesture, geo_conf = sign_detector.detect_gesture(landmarks)

        # === 3. Pick the best detection ===
        # ML model handles: open_palm, fist, thumbs_up, thumbs_down, peace, ily, pointing
        # Geometric handles EXTRA: pinch, ok_sign, horns, call_me, three_up, thumb_index_l, flat_down, four_up
        _ML_KNOWN = {'open_palm', 'fist', 'thumbs_up', 'thumbs_down', 'peace', 'ily', 'pointing'}

        gesture, conf, source = None, 0.0, None

        # For gestures ONLY geometric knows, always use geometric
        if geo_gesture and geo_conf >= 0.55 and geo_gesture not in _ML_KNOWN:
            gesture, conf, source = geo_gesture, geo_conf, 'geo'
        # For gestures ML knows, prefer ML (more accurate); fall back to geometric
        elif ml_gesture and ml_conf >= 0.50:
            gesture, conf, source = ml_gesture, ml_conf, 'ml'
        elif geo_gesture and geo_conf >= 0.65:
            gesture, conf, source = geo_gesture, geo_conf, 'geo'

        # === 4. Buffer frames for motion-based detection ===
        state['frame_buffer'].append(landmarks)
        if len(state['frame_buffer']) > 30:
            state['frame_buffer'] = state['frame_buffer'][-30:]

        # === 5. STABILITY CHECK — require same gesture for 2+ consecutive frames ===
        if gesture and conf >= 0.50:
            if gesture == state.get('last_gesture'):
                state['gesture_hold_count'] = state.get('gesture_hold_count', 0) + 1
            else:
                state['last_gesture'] = gesture
                state['gesture_hold_count'] = 1

            # Must hold gesture stable for at least 2 consecutive frames (~400ms)
            if state['gesture_hold_count'] < 2:
                emit('detection', {'status': 'collecting', 'hint': gesture, 'frames': state['gesture_hold_count']})
                return

            word = get_word_for_gesture(gesture, state.get('department'))

            # === 6. HISTORY DEDUP — block word if seen in last 5 seconds ===
            history = state.get('word_history', [])
            history = [(w, t) for w, t in history if (now - t) < 5.0]
            state['word_history'] = history

            recent_words = [w for w, t in history]
            cooldown_ok = (now - state['last_prediction_time']) > 1.5

            if cooldown_ok and word not in recent_words:
                state['last_prediction_time'] = now
                state['last_word'] = word
                state['word_history'].append((word, now))
                state['frame_buffer'] = []
                emit('detection', {
                    'type': 'word',
                    'word': word,
                    'gesture': gesture,
                    'confidence': round(conf, 3),
                    'source': source,
                })
            else:
                emit('detection', {'status': 'collecting', 'frames': len(state['frame_buffer'])})
        else:
            # No static gesture — reset hold counter
            state['gesture_hold_count'] = 0

            if len(state['frame_buffer']) >= 15:
                # Try motion-based word detection
                word, conf = sign_detector.detect_word_from_motion(state['frame_buffer'])
                if word and conf >= 0.55:
                    history = [(w, t) for w, t in state.get('word_history', []) if (now - t) < 5.0]
                    state['word_history'] = history
                    recent_words = [w for w, t in history]
                    cooldown_ok = (now - state['last_prediction_time']) > 2.0

                    if cooldown_ok and word not in recent_words:
                        state['last_prediction_time'] = now
                        state['last_word'] = word
                        state['last_gesture'] = None
                        state['word_history'].append((word, now))
                        state['frame_buffer'] = []
                        emit('detection', {
                            'type': 'word',
                            'word': word,
                            'confidence': round(conf, 3),
                            'source': 'motion',
                        })
                    else:
                        emit('detection', {'status': 'collecting', 'frames': len(state['frame_buffer'])})
                else:
                    emit('detection', {'status': 'collecting', 'frames': len(state['frame_buffer'])})
            else:
                emit('detection', {'status': 'collecting', 'frames': len(state['frame_buffer'])})


# ─── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"  🏥  Deaf AI Healthcare Assistant")
    print(f"  Hospital: {config.HOSPITAL_NAME}")
    print(f"  AI Provider: {chatbot.provider}")
    print(f"{'='*60}")
    print(f"\n  📱 Kiosk (Part 1):    http://localhost:5000/")
    print(f"  🏥 Staff Dashboard:   http://localhost:5000/staff")
    print(f"  🔄 Translator (Part 2): Opens from staff dashboard")
    print(f"  🤟 Sign Detection:    WebSocket on /socket.io/")
    print(f"\n{'='*60}\n")
    socketio.run(app, debug=config.DEBUG, host='0.0.0.0', port=5000)
