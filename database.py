import sqlite3
import json
import os
import config
import uuid
from datetime import datetime


def get_db():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            location TEXT,
            floor INTEGER DEFAULT 0,
            lat REAL,
            lng REAL,
            keywords TEXT,
            directions TEXT
        );

        CREATE TABLE IF NOT EXISTS medical_staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT,
            department_id INTEGER,
            available INTEGER DEFAULT 1,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        );

        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT DEFAULT 'Patient',
            receipt_number TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            department_id INTEGER,
            staff_id INTEGER,
            status TEXT DEFAULT 'waiting',
            triage_summary TEXT,
            triage_answers TEXT,
            communication_pref TEXT DEFAULT 'sign',
            FOREIGN KEY (department_id) REFERENCES departments(id),
            FOREIGN KEY (staff_id) REFERENCES medical_staff(id)
        );

        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            staff_id INTEGER,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            notes TEXT,
            transcript TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (staff_id) REFERENCES medical_staff(id)
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            department_id INTEGER,
            staff_id INTEGER,
            appointment_date TEXT,
            appointment_time TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (department_id) REFERENCES departments(id)
        );

        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            consultation_id INTEGER,
            medication TEXT,
            dosage TEXT,
            instructions TEXT,
            pharmacist_notified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (consultation_id) REFERENCES consultations(id)
        );
    ''')

    # Seed departments if empty
    if cursor.execute("SELECT COUNT(*) FROM departments").fetchone()[0] == 0:
        departments = [
            ('General Practice', 'General health checkups and consultations', 'Block A, Room 101', 1, -33.9135, 18.8601,
             'checkup,general,fever,cold,flu,cough,fatigue,routine',
             'From main entrance, go straight ahead past reception. Take the stairs or lift to Floor 1. Turn right, Room 101 is the third door on your left.'),
            ('Emergency Department', 'Urgent and emergency medical care', 'Block A, Ground Floor', 0, -33.9136, 18.8600,
             'emergency,urgent,accident,bleeding,unconscious,severe,critical',
             'From main entrance, turn LEFT immediately. Follow the red signs marked "Emergency". The Emergency Department is through the double doors at the end of the corridor.'),
            ('Cardiology', 'Heart and cardiovascular care', 'Block B, Room 201', 2, -33.9138, 18.8605,
             'heart,chest,blood pressure,palpitations,cardiac,cardiovascular',
             'From main entrance, go straight and exit through the back door into the courtyard. Enter Block B opposite. Take the lift to Floor 2. Room 201 is on the right.'),
            ('Orthopedics', 'Bone, joint and muscle care', 'Block B, Room 105', 1, -33.9139, 18.8604,
             'bone,joint,muscle,fracture,sprain,back pain,knee,shoulder,hip',
             'From main entrance, go straight and exit through the back door into the courtyard. Enter Block B opposite. Take the stairs to Floor 1. Room 105 is at the end of the corridor on the left.'),
            ('Dermatology', 'Skin conditions and treatment', 'Block C, Room 301', 3, -33.9140, 18.8606,
             'skin,rash,itch,acne,eczema,wound,burn,allergy skin',
             'From main entrance, turn right and walk along the covered walkway to Block C. Take the lift to Floor 3. Exit lift, turn left. Room 301 is the first door on your right.'),
            ('Ophthalmology', 'Eye care and vision', 'Block C, Room 202', 2, -33.9141, 18.8607,
             'eye,vision,blind,blurry,glasses,cataract',
             'From main entrance, turn right and walk along the covered walkway to Block C. Take the lift to Floor 2. Turn right, Room 202 is the second door on your left.'),
            ('ENT', 'Ear, Nose and Throat care', 'Block C, Room 203', 2, -33.9141, 18.8608,
             'ear,nose,throat,hearing,sinus,tonsil,voice,swallow',
             'From main entrance, turn right and walk along the covered walkway to Block C. Take the lift to Floor 2. Turn right, Room 203 is the third door on your left (next to Ophthalmology).'),
            ('Neurology', 'Brain and nervous system care', 'Block D, Room 401', 4, -33.9142, 18.8609,
             'headache,migraine,dizzy,numbness,seizure,memory,nerve,brain',
             'From main entrance, go straight past reception, turn left at the cafeteria. Follow signs to Block D. Take the lift to Floor 4. Room 401 is directly ahead when you exit the lift.'),
            ('Psychiatry & Mental Health', 'Mental health and wellness', 'Block D, Room 105', 1, -33.9143, 18.8610,
             'mental,anxiety,depression,stress,sleep,panic,mood,counseling',
             'From main entrance, go straight past reception, turn left at the cafeteria. Follow signs to Block D. Take the stairs to Floor 1. Room 105 is the quiet wing at the far end of the corridor.'),
            ('Gastroenterology', 'Digestive system care', 'Block B, Room 302', 3, -33.9138, 18.8606,
             'stomach,nausea,vomit,diarrhea,digestion,abdomen,liver',
             'From main entrance, go straight and exit through the back door into the courtyard. Enter Block B opposite. Take the lift to Floor 3. Turn left, Room 302 is the second door on your right.'),
            ('Pulmonology', 'Lung and respiratory care', 'Block B, Room 303', 3, -33.9138, 18.8607,
             'breathing,lung,asthma,cough,respiratory,chest,wheeze',
             'From main entrance, go straight and exit through the back door into the courtyard. Enter Block B opposite. Take the lift to Floor 3. Turn left, Room 303 is the third door on your right.'),
            ('Pharmacy', 'Medication dispensary', 'Block A, Ground Floor', 0, -33.9134, 18.8602,
             'medication,prescription,pharmacy,medicine,drug',
             'From main entrance, turn RIGHT immediately. Walk past the waiting area. The Pharmacy counter is at the end of the hall with green signage.'),
        ]
        cursor.executemany(
            'INSERT INTO departments (name, description, location, floor, lat, lng, keywords, directions) VALUES (?,?,?,?,?,?,?,?)',
            departments
        )

    # Seed medical staff if empty
    if cursor.execute("SELECT COUNT(*) FROM medical_staff").fetchone()[0] == 0:
        staff = [
            ('Dr. Naledi Mokoena', 'General Practitioner', 1),
            ('Dr. Sipho Nkosi', 'Emergency Physician', 2),
            ('Dr. Amahle Dlamini', 'Cardiologist', 3),
            ('Dr. Thabo Molefe', 'Orthopedic Surgeon', 4),
            ('Dr. Zanele Khumalo', 'Dermatologist', 5),
            ('Dr. Bongani Mthembu', 'Ophthalmologist', 6),
            ('Dr. Lerato Mahlangu', 'ENT Specialist', 7),
            ('Dr. Nompumelelo Zuma', 'Neurologist', 8),
            ('Dr. Kagiso Patel', 'Psychiatrist', 9),
            ('Dr. Thandiwe Ngcobo', 'Gastroenterologist', 10),
            ('Dr. Mandla Sithole', 'Pulmonologist', 11),
            ('Sr. Nomsa Cele', 'Nurse - General', 1),
            ('Sr. Palesa Ndaba', 'Nurse - Emergency', 2),
        ]
        cursor.executemany(
            'INSERT INTO medical_staff (name, title, department_id) VALUES (?,?,?)',
            staff
        )

    conn.commit()
    conn.close()


def generate_receipt_number():
    return 'TH-' + uuid.uuid4().hex[:8].upper()


def create_patient(name, department_id, triage_summary, triage_answers, communication_pref='sign'):
    conn = get_db()
    receipt = generate_receipt_number()
    # Find available staff in department
    staff = conn.execute(
        'SELECT id FROM medical_staff WHERE department_id = ? AND available = 1 LIMIT 1',
        (department_id,)
    ).fetchone()
    staff_id = staff['id'] if staff else None

    conn.execute(
        '''INSERT INTO patients (name, receipt_number, department_id, staff_id, status, 
           triage_summary, triage_answers, communication_pref)
           VALUES (?, ?, ?, ?, 'waiting', ?, ?, ?)''',
        (name, receipt, department_id, staff_id, triage_summary,
         json.dumps(triage_answers), communication_pref)
    )
    conn.commit()
    patient_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
    conn.close()
    return dict(patient)


def match_department(symptoms_text):
    conn = get_db()
    departments = conn.execute('SELECT * FROM departments').fetchall()
    conn.close()

    symptoms_lower = symptoms_text.lower()
    best_match = None
    best_score = 0

    for dept in departments:
        keywords = dept['keywords'].split(',')
        score = sum(1 for kw in keywords if kw.strip() in symptoms_lower)
        if score > best_score:
            best_score = score
            best_match = dict(dept)

    # Default to General Practice
    if best_match is None or best_score == 0:
        conn = get_db()
        gp = conn.execute('SELECT * FROM departments WHERE id = 1').fetchone()
        conn.close()
        best_match = dict(gp)

    return best_match


def get_waiting_patients():
    conn = get_db()
    patients = conn.execute('''
        SELECT p.*, d.name as department_name, d.location as department_location,
               m.name as staff_name, m.title as staff_title
        FROM patients p
        LEFT JOIN departments d ON p.department_id = d.id
        LEFT JOIN medical_staff m ON p.staff_id = m.id
        WHERE p.status = 'waiting'
        ORDER BY p.created_at DESC
    ''').fetchall()
    conn.close()
    return [dict(p) for p in patients]


def receive_patient(patient_id, staff_id=None):
    conn = get_db()
    if staff_id:
        conn.execute('UPDATE patients SET status = ?, staff_id = ? WHERE id = ?',
                      ('in_consultation', staff_id, patient_id))
    else:
        conn.execute('UPDATE patients SET status = ? WHERE id = ?',
                      ('in_consultation', patient_id))
    conn.commit()
    patient = conn.execute('''
        SELECT p.*, d.name as department_name, m.name as staff_name
        FROM patients p
        LEFT JOIN departments d ON p.department_id = d.id
        LEFT JOIN medical_staff m ON p.staff_id = m.id
        WHERE p.id = ?
    ''', (patient_id,)).fetchone()
    conn.close()
    return dict(patient) if patient else None


def start_consultation(patient_id, staff_id):
    conn = get_db()
    conn.execute(
        'INSERT INTO consultations (patient_id, staff_id, started_at, transcript) VALUES (?, ?, ?, ?)',
        (patient_id, staff_id, datetime.now().isoformat(), '[]')
    )
    conn.commit()
    cid = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return cid


def save_consultation_message(consultation_id, sender, message):
    conn = get_db()
    row = conn.execute('SELECT transcript FROM consultations WHERE id = ?', (consultation_id,)).fetchone()
    if row:
        transcript = json.loads(row['transcript'] or '[]')
        transcript.append({
            'sender': sender,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        conn.execute('UPDATE consultations SET transcript = ? WHERE id = ?',
                      (json.dumps(transcript), consultation_id))
        conn.commit()
    conn.close()


def create_appointment(patient_id, department_id, staff_id, date, time, notes=''):
    conn = get_db()
    conn.execute(
        'INSERT INTO appointments (patient_id, department_id, staff_id, appointment_date, appointment_time, notes) VALUES (?,?,?,?,?,?)',
        (patient_id, department_id, staff_id, date, time, notes)
    )
    conn.commit()
    apt_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    apt = conn.execute('SELECT * FROM appointments WHERE id = ?', (apt_id,)).fetchone()
    conn.close()
    return dict(apt)


def create_prescription(patient_id, consultation_id, medication, dosage, instructions):
    conn = get_db()
    conn.execute(
        'INSERT INTO prescriptions (patient_id, consultation_id, medication, dosage, instructions) VALUES (?,?,?,?,?)',
        (patient_id, consultation_id, medication, dosage, instructions)
    )
    conn.commit()
    pid = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return pid


def get_patient(patient_id):
    conn = get_db()
    patient = conn.execute('''
        SELECT p.*, d.name as department_name, d.location as department_location,
               m.name as staff_name, m.title as staff_title
        FROM patients p
        LEFT JOIN departments d ON p.department_id = d.id
        LEFT JOIN medical_staff m ON p.staff_id = m.id
        WHERE p.id = ?
    ''', (patient_id,)).fetchone()
    conn.close()
    return dict(patient) if patient else None


def get_all_departments():
    conn = get_db()
    depts = conn.execute('SELECT * FROM departments').fetchall()
    conn.close()
    return [dict(d) for d in depts]


def get_all_patients():
    """Get all patients with department and staff info."""
    conn = get_db()
    patients = conn.execute('''
        SELECT p.*, d.name as department_name, d.location as department_location,
               m.name as staff_name, m.title as staff_title
        FROM patients p
        LEFT JOIN departments d ON p.department_id = d.id
        LEFT JOIN medical_staff m ON p.staff_id = m.id
        ORDER BY p.created_at DESC
    ''').fetchall()
    conn.close()
    return [dict(p) for p in patients]


def complete_patient(patient_id):
    """Mark a patient consultation as completed."""
    conn = get_db()
    conn.execute("UPDATE patients SET status = 'completed' WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()


def get_department_staff(department_id):
    conn = get_db()
    staff = conn.execute(
        'SELECT * FROM medical_staff WHERE department_id = ?', (department_id,)
    ).fetchall()
    conn.close()
    return [dict(s) for s in staff]
