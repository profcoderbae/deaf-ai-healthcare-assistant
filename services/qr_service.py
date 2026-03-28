import qrcode
import io
import base64
import json
import config


def generate_qr_base64(data_string):
    """Generate a QR code and return as base64 PNG string."""
    qr = qrcode.QRCode(version=1, box_size=10, border=4,
                        error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(data_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def generate_directions_qr(department):
    """Generate QR code with Google Maps directions to department."""
    lat = department.get('lat', config.HOSPITAL_LAT)
    lng = department.get('lng', config.HOSPITAL_LNG)
    location_name = department.get('location', '')
    dept_name = department.get('name', '')

    maps_url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&destination={lat},{lng}"
        f"&travelmode=walking"
    )

    qr_data = json.dumps({
        "type": "directions",
        "hospital": config.HOSPITAL_NAME,
        "department": dept_name,
        "location": location_name,
        "maps_url": maps_url,
        "lat": lat,
        "lng": lng,
    })

    return {
        "qr_image": generate_qr_base64(maps_url),
        "maps_url": maps_url,
        "department": dept_name,
        "location": location_name,
    }


def generate_appointment_qr(patient_name, receipt_number, appointment_date,
                              appointment_time, department_name, doctor_name, notes=''):
    """Generate QR code with appointment details."""
    appointment_data = {
        "type": "appointment",
        "hospital": config.HOSPITAL_NAME,
        "patient": patient_name,
        "receipt": receipt_number,
        "date": appointment_date,
        "time": appointment_time,
        "department": department_name,
        "doctor": doctor_name,
        "notes": notes,
    }

    display_text = (
        f"APPOINTMENT - {config.HOSPITAL_NAME}\n"
        f"Patient: {patient_name}\n"
        f"Receipt: {receipt_number}\n"
        f"Date: {appointment_date} at {appointment_time}\n"
        f"Department: {department_name}\n"
        f"Doctor: {doctor_name}\n"
        f"Notes: {notes}"
    )

    return {
        "qr_image": generate_qr_base64(json.dumps(appointment_data)),
        "data": appointment_data,
        "display_text": display_text,
    }


def generate_prescription_qr(patient_name, receipt_number, medication,
                               dosage, instructions, doctor_name):
    """Generate QR code with prescription details for pharmacy."""
    prescription_data = {
        "type": "prescription",
        "hospital": config.HOSPITAL_NAME,
        "patient": patient_name,
        "receipt": receipt_number,
        "medication": medication,
        "dosage": dosage,
        "instructions": instructions,
        "prescribed_by": doctor_name,
    }

    return {
        "qr_image": generate_qr_base64(json.dumps(prescription_data)),
        "data": prescription_data,
    }
