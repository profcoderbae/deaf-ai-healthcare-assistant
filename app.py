from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
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

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
CORS(app)

chatbot = HealthcareChatbot()

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
    print(f"\n{'='*60}\n")
    app.run(debug=config.DEBUG, host='0.0.0.0', port=5000)
