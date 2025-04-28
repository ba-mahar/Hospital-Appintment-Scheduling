from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
from models.models import Service, Doctor, Appointment, User
from models.db import db

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session or session['role'] != 'patient':
        flash('Please login as patient to book appointment', 'danger')
        return redirect(url_for('auth.login'))
    
    services = Service.get_all_services()
    doctors = Doctor.get_all_doctors()
    
    if request.method == 'POST':
        service_id = request.form.get('service_id')
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        start_time = request.form.get('start_time')
        notes = request.form.get('notes')
        
        if not all([service_id, doctor_id, appointment_date, start_time]):
            flash('Please fill all required fields', 'danger')
            return redirect(url_for('appointments.book'))
        
        # Calculate end time based on service duration
        service = Service.get_service_by_id(service_id)
        if not service:
            flash('Invalid service selected', 'danger')
            return redirect(url_for('appointments.book'))
        
        start_datetime = datetime.strptime(start_time, '%H:%M')
        end_datetime = start_datetime + timedelta(minutes=service['duration'])
        end_time = end_datetime.strftime('%H:%M')
        
        # Create appointment
        if Appointment.create_appointment(
            patient_id=session['user_id'],
            doctor_id=doctor_id,
            service_id=service_id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            notes=notes
        ):
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('patient.dashboard'))
        else:
            flash('Failed to book appointment. Please try again.', 'danger')
            return redirect(url_for('appointments.book'))
    
    return render_template('appointment.html', services=services, doctors=doctors)

@appointments_bp.route('/get_available_slots', methods=['POST'])
def get_available_slots():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    doctor_id = request.form.get('doctor_id')
    date = request.form.get('date')
    service_id = request.form.get('service_id')
    
    if not all([doctor_id, date, service_id]):
        return jsonify({'error': 'Missing parameters'}), 400
    
    slots = Appointment.get_available_slots(doctor_id, date, service_id)
    return jsonify({'slots': slots})

@appointments_bp.route('/cancel/<int:appointment_id>', methods=['POST'])
def cancel(appointment_id):
    if 'user_id' not in session:
        flash('Please login to cancel appointment', 'danger')
        return redirect(url_for('auth.login'))
    
    appointment = Appointment.get_appointment_by_id(appointment_id)
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('index'))
    
    # Check if user owns the appointment or is admin/staff
    if session['role'] == 'patient' and appointment['patient_id'] != session['user_id']:
        flash('You are not authorized to cancel this appointment', 'danger')
        return redirect(url_for('index'))
    
    if Appointment.update_appointment_status(appointment_id, 'cancelled'):
        flash('Appointment cancelled successfully', 'success')
    else:
        flash('Failed to cancel appointment', 'danger')
    
    if session['role'] == 'patient':
        return redirect(url_for('patient.dashboard'))
    else:
        return redirect(url_for('admin.appointments'))