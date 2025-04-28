from datetime import datetime
from .db import db

class User:
    @staticmethod
    def create_table():
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
        CREATE TABLE users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            username NVARCHAR(50) UNIQUE NOT NULL,
            password NVARCHAR(255) NOT NULL,
            email NVARCHAR(100) UNIQUE NOT NULL,
            full_name NVARCHAR(100) NOT NULL,
            phone NVARCHAR(20),
            role NVARCHAR(20) NOT NULL CHECK (role IN ('admin', 'doctor', 'staff', 'patient')),
            created_at DATETIME DEFAULT GETDATE(),
            is_active BIT DEFAULT 1
        )
        """
        return db.execute_query(query)

    @staticmethod
    def create_user(username, password, email, full_name, role, phone=None):
        query = """
        INSERT INTO users (username, password, email, full_name, phone, role)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return db.execute_query(query, (username, password, email, full_name, phone, role))

    @staticmethod
    def get_user_by_username(username):
        query = "SELECT * FROM users WHERE username = ?"
        result = db.execute_query(query, (username,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def get_user_by_id(user_id):
        query = "SELECT * FROM users WHERE id = ?"
        result = db.execute_query(query, (user_id,), fetch=True)
        return result[0] if result else None


class Patient:
    @staticmethod
    def create_table():
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='patients' AND xtype='U')
        CREATE TABLE patients (
            id INT IDENTITY(1,1) PRIMARY KEY,
            user_id INT UNIQUE NOT NULL,
            dob DATE,
            gender NVARCHAR(10),
            address NVARCHAR(255),
            emergency_contact NVARCHAR(20),
            medical_history TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        return db.execute_query(query)

    @staticmethod
    def create_patient(user_id, dob=None, gender=None, address=None, emergency_contact=None, medical_history=None):
        query = """
        INSERT INTO patients (user_id, dob, gender, address, emergency_contact, medical_history)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return db.execute_query(query, (user_id, dob, gender, address, emergency_contact, medical_history))

    @staticmethod
    def get_patient_by_user_id(user_id):
        query = """
        SELECT p.*, u.full_name, u.email, u.phone 
        FROM patients p 
        JOIN users u ON p.user_id = u.id 
        WHERE p.user_id = ?
        """
        result = db.execute_query(query, (user_id,), fetch=True)
        return result[0] if result else None


class Doctor:
    @staticmethod
    def create_table():
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='doctors' AND xtype='U')
        CREATE TABLE doctors (
            id INT IDENTITY(1,1) PRIMARY KEY,
            user_id INT UNIQUE NOT NULL,
            specialization NVARCHAR(100) NOT NULL,
            qualification NVARCHAR(100) NOT NULL,
            available_days NVARCHAR(50) NOT NULL,
            available_time_start TIME NOT NULL,
            available_time_end TIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        return db.execute_query(query)

    @staticmethod
    def create_doctor(user_id, specialization, qualification, available_days, available_time_start, available_time_end):
        query = """
        INSERT INTO doctors (user_id, specialization, qualification, available_days, available_time_start, available_time_end)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return db.execute_query(query, (user_id, specialization, qualification, available_days, available_time_start, available_time_end))

    @staticmethod
    def get_all_doctors():
        query = """
        SELECT d.*, u.full_name, u.email, u.phone 
        FROM doctors d 
        JOIN users u ON d.user_id = u.id 
        WHERE u.is_active = 1
        """
        return db.execute_query(query, fetch=True)

    @staticmethod
    def get_doctor_by_id(doctor_id):
        query = """
        SELECT d.*, u.full_name, u.email, u.phone 
        FROM doctors d 
        JOIN users u ON d.user_id = u.id 
        WHERE d.id = ? AND u.is_active = 1
        """
        result = db.execute_query(query, (doctor_id,), fetch=True)
        return result[0] if result else None


class Service:
    @staticmethod
    def create_table():
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='services' AND xtype='U')
        CREATE TABLE services (
            id INT IDENTITY(1,1) PRIMARY KEY,
            name NVARCHAR(100) NOT NULL,
            description TEXT,
            duration INT NOT NULL, -- in minutes
            price DECIMAL(10, 2) NOT NULL,
            is_active BIT DEFAULT 1
        )
        """
        return db.execute_query(query)

    @staticmethod
    def create_service(name, description, duration, price):
        query = """
        INSERT INTO services (name, description, duration, price)
        VALUES (?, ?, ?, ?)
        """
        return db.execute_query(query, (name, description, duration, price))

    @staticmethod
    def get_all_services():
        query = "SELECT * FROM services WHERE is_active = 1"
        return db.execute_query(query, fetch=True)

    @staticmethod
    def get_service_by_id(service_id):
        query = "SELECT * FROM services WHERE id = ? AND is_active = 1"
        result = db.execute_query(query, (service_id,), fetch=True)
        return result[0] if result else None


class Appointment:
    @staticmethod
    def create_table():
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='appointments' AND xtype='U')
        CREATE TABLE appointments (
            id INT IDENTITY(1,1) PRIMARY KEY,
            patient_id INT NOT NULL,
            doctor_id INT,
            service_id INT NOT NULL,
            appointment_date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            status NVARCHAR(20) NOT NULL CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no-show')) DEFAULT 'scheduled',
            notes TEXT,
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (patient_id) REFERENCES users(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
        """
        return db.execute_query(query)

    @staticmethod
    def create_appointment(patient_id, doctor_id, service_id, appointment_date, start_time, end_time, notes=None):
        query = """
        INSERT INTO appointments (patient_id, doctor_id, service_id, appointment_date, start_time, end_time, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return db.execute_query(query, (patient_id, doctor_id, service_id, appointment_date, start_time, end_time, notes))

    @staticmethod
    def get_appointment_by_id(appointment_id):
        query = """
        SELECT a.*, 
               u.full_name AS patient_name, 
               d.user_id AS doctor_user_id, 
               ud.full_name AS doctor_name,
               s.name AS service_name
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        LEFT JOIN doctors d ON a.doctor_id = d.id
        LEFT JOIN users ud ON d.user_id = ud.id
        JOIN services s ON a.service_id = s.id
        WHERE a.id = ?
        """
        result = db.execute_query(query, (appointment_id,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def get_patient_appointments(patient_id):
        query = """
        SELECT a.*, 
               d.user_id AS doctor_user_id, 
               ud.full_name AS doctor_name,
               s.name AS service_name
        FROM appointments a
        LEFT JOIN doctors d ON a.doctor_id = d.id
        LEFT JOIN users ud ON d.user_id = ud.id
        JOIN services s ON a.service_id = s.id
        WHERE a.patient_id = ?
        ORDER BY a.appointment_date DESC, a.start_time DESC
        """
        return db.execute_query(query, (patient_id,), fetch=True)

    @staticmethod
    def get_doctor_appointments(doctor_id):
        query = """
        SELECT a.*, 
               u.full_name AS patient_name,
               s.name AS service_name
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        JOIN services s ON a.service_id = s.id
        WHERE a.doctor_id = ? AND a.appointment_date >= CAST(GETDATE() AS DATE)
        ORDER BY a.appointment_date, a.start_time
        """
        return db.execute_query(query, (doctor_id,), fetch=True)

    @staticmethod
    def get_all_appointments(date=None):
        base_query = """
        SELECT a.*, 
               u.full_name AS patient_name, 
               d.user_id AS doctor_user_id, 
               ud.full_name AS doctor_name,
               s.name AS service_name
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        LEFT JOIN doctors d ON a.doctor_id = d.id
        LEFT JOIN users ud ON d.user_id = ud.id
        JOIN services s ON a.service_id = s.id
        """
        
        if date:
            query = base_query + " WHERE a.appointment_date = ? ORDER BY a.appointment_date, a.start_time"
            return db.execute_query(query, (date,), fetch=True)
        else:
            query = base_query + " ORDER BY a.appointment_date DESC, a.start_time DESC"
            return db.execute_query(query, fetch=True)

    @staticmethod
    def update_appointment_status(appointment_id, status):
        query = "UPDATE appointments SET status = ? WHERE id = ?"
        return db.execute_query(query, (status, appointment_id))

    @staticmethod
    def get_available_slots(doctor_id, date, service_id):
        # Get doctor's availability
        doctor = Doctor.get_doctor_by_id(doctor_id)
        if not doctor:
            return []

        # Get service duration
        service = Service.get_service_by_id(service_id)
        if not service:
            return []

        # Check if the requested date is in doctor's available days
        available_days = doctor['available_days'].split(',')
        day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
        if day_name not in available_days:
            return []

        # Get existing appointments for the doctor on that day
        query = """
        SELECT start_time, end_time 
        FROM appointments 
        WHERE doctor_id = ? AND appointment_date = ? AND status != 'cancelled'
        ORDER BY start_time
        """
        booked_slots = db.execute_query(query, (doctor_id, date), fetch=True)

        # Generate available slots
        start_time = datetime.strptime(doctor['available_time_start'], '%H:%M:%S')
        end_time = datetime.strptime(doctor['available_time_end'], '%H:%M:%S')
        slot_duration = service['duration']
        available_slots = []

        current_time = start_time
        while current_time + timedelta(minutes=slot_duration) <= end_time:
            slot_end = current_time + timedelta(minutes=slot_duration)
            slot_available = True

            # Check against booked slots
            for slot in booked_slots:
                slot_start = datetime.strptime(slot['start_time'], '%H:%M:%S')
                slot_end_existing = datetime.strptime(slot['end_time'], '%H:%M:%S')
                
                if not (slot_end <= slot_start or current_time >= slot_end_existing):
                    slot_available = False
                    break

            if slot_available:
                available_slots.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': slot_end.strftime('%H:%M')
                })

            current_time += timedelta(minutes=15)  # Next slot starts every 15 minutes

        return available_slots