# database.py
import sqlite3
import hashlib
import os

def init_db():
    db_file = 'school.db'
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    # Tabla de usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                ci TEXT PRIMARY KEY,
                name TEXT,
                password TEXT,
                role TEXT,
                year INTEGER,
                section TEXT)''')
    
    # Tabla de horarios mejorada
    c.execute('''CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                section TEXT,
                day TEXT,
                hour1 TEXT,
                hour2 TEXT,
                hour3 TEXT,
                hour4 TEXT,
                hour5 TEXT,
                hour6 TEXT)''')
    
    # Crear usuario coordinador de ejemplo
    try:
        coordinator_ci = "12345678"
        coordinator_name = "Ana Coordinadora"
        coordinator_pass = hashlib.sha256("CoordSecure123!".encode()).hexdigest()
        c.execute("INSERT INTO users (ci, name, password, role) VALUES (?, ?, ?, ?)", 
                 (coordinator_ci, coordinator_name, coordinator_pass, "coordinator"))
    except sqlite3.IntegrityError:
        pass
    
    # Crear usuario estudiante de ejemplo
    try:
        student_ci = "87654321"
        student_name = "Carlos Estudiante"
        student_pass = hashlib.sha256("student123".encode()).hexdigest()
        c.execute("INSERT INTO users (ci, name, password, role, year, section) VALUES (?, ?, ?, ?, ?, ?)", 
                 (student_ci, student_name, student_pass, "student", 1, "A"))
    except sqlite3.IntegrityError:
        pass
        
    conn.commit()
    conn.close()

def verify_user(ci, password):
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    hashed_pass = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE ci = ? AND password = ?", (ci, hashed_pass))
    user = c.fetchone()
    conn.close()
    return user

def get_schedule(year, section):
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute("SELECT * FROM schedules WHERE year = ? AND section = ?", (year, section))
    schedules = c.fetchall()
    conn.close()
    return schedules

def save_schedule(data):
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    
    # Eliminar horario existente para este día si existe
    c.execute("DELETE FROM schedules WHERE year = ? AND section = ? AND day = ?", 
             (data[0], data[1], data[2]))
    
    # Insertar nuevo horario
    c.execute('''INSERT INTO schedules 
              (year, section, day, hour1, hour2, hour3, hour4, hour5, hour6)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()

def register_student(ci, name, year, section, password):
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    hashed_pass = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (ci, name, password, role, year, section) VALUES (?, ?, ?, ?, ?, ?)", 
                 (ci, name, hashed_pass, "student", year, section))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Inicializar la base de datos
init_db()