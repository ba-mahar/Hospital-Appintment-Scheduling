from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.models import Appointment, Patient

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session['role'] != 'patient':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    patient = Patient.get_patient_by_user_id(session['user_id'])
    appointments = Appointment.get_patient_appointments(session['user_id'])
    
    return render_template('patient-dashboard.html', patient=patient, appointments=appointments)