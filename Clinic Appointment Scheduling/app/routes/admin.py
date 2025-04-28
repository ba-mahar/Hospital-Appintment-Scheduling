from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.models import User, Doctor, Service, Appointment
from models.db import db
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get today's appointments
    today = datetime.now().strftime('%Y-%m-%d')
    appointments = Appointment.get_all_appointments(today)
    
    # Count stats
    total_patients = len(User.get_all_patients())
    total_doctors = len(Doctor.get_all_doctors())
    pending_appointments = len([a for a in appointments if a['status'] == 'scheduled'])
    
    return render_template('admin-dashboard.html', 
                         appointments=appointments,
                         total_patients=total_patients,
                         total_doctors=total_doctors,
                         pending_appointments=pending_appointments)

@admin_bp.route('/appointments')
def appointments():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    date = request.args.get('date')
    if date:
        appointments = Appointment.get_all_appointments(date)
    else:
        appointments = Appointment.get_all_appointments()
    
    return render_template('admin-appointments.html', appointments=appointments)

@admin_bp.route('/doctors')
def doctors():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    doctors = Doctor.get_all_doctors()
    return render_template('admin-doctors.html', doctors=doctors)

@admin_bp.route('/add-doctor', methods=['GET', 'POST'])
def add_doctor():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        specialization = request.form.get('specialization')
        qualification = request.form.get('qualification')
        available_days = ','.join(request.form.getlist('available_days'))
        available_time_start = request.form.get('available_time_start')
        available_time_end = request.form.get('available_time_end')
        
        # Validate input
        if not all([username, email, full_name, password, specialization, qualification, available_days, available_time_start, available_time_end]):
            flash('Please fill all required fields', 'danger')
            return redirect(url_for('admin.add_doctor'))
        
        # Check if username or email exists
        if User.get_user_by_username(username):
            flash('Username already exists', 'danger')
            return redirect(url_for('admin.add_doctor'))
        
        if User.get_user_by_email(email):
            flash('Email already exists', 'danger')
            return redirect(url_for('admin.add_doctor'))
        
        # Create user
        hashed_password = generate_password_hash(password)
        if User.create_user(username, hashed_password, email, full_name, 'doctor', phone):
            user = User.get_user_by_username(username)
            # Create doctor
            if Doctor.create_doctor(
                user_id=user['id'],
                specialization=specialization,
                qualification=qualification,
                available_days=available_days,
                available_time_start=available_time_start,
                available_time_end=available_time_end
            ):
                flash('Doctor added successfully', 'success')
                return redirect(url_for('admin.doctors'))
            else:
                # Rollback user creation if doctor creation fails
                User.delete_user(user['id'])
                flash('Failed to add doctor. Please try again.', 'danger')
        else:
            flash('Failed to add doctor. Please try again.', 'danger')
    
    return render_template('admin-add-doctor.html')

@admin_bp.route('/services')
def services():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    services = Service.get_all_services()
    return render_template('admin-services.html', services=services)

@admin_bp.route('/add-service', methods=['GET', 'POST'])
def add_service():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        duration = request.form.get('duration')
        price = request.form.get('price')
        
        if not all([name, duration, price]):
            flash('Please fill all required fields', 'danger')
            return redirect(url_for('admin.add_service'))
        
        if Service.create_service(name, description, int(duration), float(price)):
            flash('Service added successfully', 'success')
            return redirect(url_for('admin.services'))
        else:
            flash('Failed to add service. Please try again.', 'danger')
    
    return render_template('admin-add-service.html')

@admin_bp.route('/patients')
def patients():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    patients = User.get_all_patients()
    return render_template('admin-patients.html', patients=patients)