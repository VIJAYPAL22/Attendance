import random
import string
from datetime import datetime, timedelta
from flask_mail import Message
from flask import current_app
from .extensions import mail
from .models import db, Employee

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(employee_email, employee_name, code):
    subject = "Your HRM System Verification Code"
    body = f"""
    Hello {employee_name},

    Your verification code for HRM System is: {code}

    This code will expire in 24 hours.

    If you didn't request this, please contact your administrator.
    """
    sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'your_email@example.com')
    msg = Message(subject, sender=sender, recipients=[employee_email], body=body)
    mail.send(msg)

def set_verification_code(emp_id):
    employee = Employee.query.get(emp_id)
    if not employee:
        return None
    code = generate_verification_code()
    employee.verification_code = code
    employee.code_expiry = datetime.today() + timedelta(hours=24)
    db.session.commit()
    send_verification_email(employee.email, employee.name, code)
    return code

def verify_code(emp_id, code):
    employee = Employee.query.get(emp_id)
    if not employee or not employee.verification_code:
        return False
    if datetime.utcnow() > employee.code_expiry:
        return False
    return employee.verification_code == code