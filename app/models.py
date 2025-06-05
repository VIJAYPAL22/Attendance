from .extensions import db
from datetime import datetime, date
from sqlalchemy import func
import pytz

def current_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).replace(second=0, microsecond=0)

class Employee(db.Model):
    emp_id = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    department = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.String(25), nullable=False)
    joining_date = db.Column(db.String(25), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    job_status = db.Column(db.String(50), nullable=False)
    f_name = db.Column(db.String(100), nullable=False)
    verification_code = db.Column(db.String(6), nullable=True)
    code_expiry = db.Column(db.DateTime, nullable=True)

class EmployeeSchema(db.Model):
    ES_id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String, db.ForeignKey('employee.emp_id'))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    department = db.Column(db.String(50))
    position = db.Column(db.String(50))
    status = db.Column(db.String(255), nullable=False)
    today_date = db.Column(db.Date, default=date.today, nullable=False)
    time = db.Column(db.Time, default=lambda: current_ist_time().time(), nullable=False)
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))

class empTime(db.Model):
    emptime_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    emp_id = db.Column(db.String, db.ForeignKey('employee.emp_id'))
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    today_date = db.Column(db.Date, default=date.today, nullable=False)
    time = db.Column(db.Time, default=lambda: current_ist_time().time(), nullable=False)

class Leaves(db.Model):
    leave_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    emp_id = db.Column(db.String, db.ForeignKey('employee.emp_id'))
    leave_type = db.Column(db.String(255), nullable=False)
    today_date = db.Column(db.Date, default=date.today, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)

class EmployeeSchemaArchive(db.Model):
    __tablename__ = 'employee_schema_archive'
    ES_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    emp_id = db.Column(db.String)
    email = db.Column(db.String(255))
    department = db.Column(db.String(255))
    position = db.Column(db.String(255))
    status = db.Column(db.String(255))
    today_date = db.Column(db.Date)
    time = db.Column(db.Time)
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))

class empTimeArchive(db.Model):
    __tablename__ = 'emp_time_archive'
    emptime_id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String)
    name = db.Column(db.String(255))
    status = db.Column(db.String(255))
    today_date = db.Column(db.Date)
    time = db.Column(db.Time)

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_reset_date = db.Column(db.Date, nullable=False, default=date.today)