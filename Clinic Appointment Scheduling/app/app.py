from flask import Flask, render_template
from config import config
from models.db import db
from models.models import User, Patient, Doctor, Service, Appointment
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.appointments import appointments_bp
    from routes.admin import admin_bp
    from routes.patient import patient_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(patient_bp)

    # Error handlers
    @app.errorhandler(404)
    def
