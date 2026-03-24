import sqlite3
import os

DB_PATH = "data/vitals.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER,
        sex TEXT,
        phone TEXT,
        email TEXT UNIQUE,
        password TEXT,
        address TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS vitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        date TEXT,
        heart_rate REAL,
        spo2 REAL,
        temperature REAL,
        bp_systolic REAL,
        bp_diastolic REAL,
        medicines TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    )''')

    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

def save_patient(patient_id, name, age, sex, phone, email, password, address):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO patients 
        (patient_id, name, age, sex, phone, email, password, address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (patient_id, name, age, sex, phone, email, password, address))
    conn.commit()
    conn.close()

def get_patient_by_email(email):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM patients WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    return row

def save_vitals(patient_id, date, heart_rate, spo2, temperature,
                bp_systolic, bp_diastolic, medicines):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO vitals 
        (patient_id, date, heart_rate, spo2, temperature,
        bp_systolic, bp_diastolic, medicines)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (patient_id, date, heart_rate, spo2, temperature,
        bp_systolic, bp_diastolic, medicines))
    conn.commit()
    conn.close()

def get_vitals_by_patient(patient_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM vitals WHERE patient_id = ? ORDER BY date ASC",
              (patient_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_vitals(patient_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM vitals WHERE patient_id = ?", (patient_id,))
    conn.commit()
    conn.close()

def delete_patient(patient_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM vitals WHERE patient_id = ?", (patient_id,))
    c.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
    conn.commit()
    conn.close()