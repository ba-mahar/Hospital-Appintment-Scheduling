from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.models import User, Patient
from models.db import db
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.get_user_by_username(username)
        
        if not user or not check_password_hash(user['password'], password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user['is_active']:
            flash('Your account is disabled. Please contact administrator.', 'danger')
            return redirect(url_for('auth.login'))
        
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session.permanent = remember

        flash('Login successful!', 'success')
        
        if user['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user['role'] == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        elif user['role'] == 'patient':
            return redirect(url_for('patient.dashboard'))
        else:
            return redirect(url_for('index'))

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, full_name, password, confirm_password]):
            flash('All fields are required except phone', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'danger')
            return redirect(url_for('auth.register'))
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address', 'danger')
            return redirect(url_for('auth.register'))
        
        # Check if username or email exists
        if User.get_user_by_username(username):
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.get_user_by_email(email):
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create user
        hashed_password = generate_password_hash(password)
        if User.create_user(username, hashed_password, email, full_name, 'patient', phone):
            user = User.get_user_by_username(username)
            Patient.create_patient(user['id'])
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Please try again.', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))