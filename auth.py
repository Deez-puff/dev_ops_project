import bcrypt
import uuid
import re
from database import save_patient, get_patient_by_email

def hash_password(password):
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must have at least one uppercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must have at least one number"
    return True, "Valid"

def is_valid_phone(phone):
    pattern = r'^\+?[\d\s\-]{10,15}$'
    return re.match(pattern, phone) is not None

def generate_patient_id():
    return "VIT-" + str(uuid.uuid4())[:8].upper()

def register_patient(name, age, sex, phone, email, password, address):
    if not is_valid_email(email):
        return False, "Invalid email address format"

    if not is_valid_phone(phone):
        return False, "Invalid phone number"

    valid, msg = is_valid_password(password)
    if not valid:
        return False, msg

    existing = get_patient_by_email(email)
    if existing:
        return False, "This email is already registered. Please login."

    patient_id = generate_patient_id()
    hashed = hash_password(password)
    save_patient(patient_id, name, age, sex, phone,
                 email, hashed, address)
    return True, patient_id

def login_patient(email, password):
    if not email or not password:
        return False, "Please enter both email and password"

    patient = get_patient_by_email(email)
    if not patient:
        return False, "No account found with this email"

    if not check_password(password, patient[6]):
        return False, "Incorrect password. Please try again."

    return True, patient