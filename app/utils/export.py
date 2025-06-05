# app/utils/export.py
import pandas as pd
import logging
from io import BytesIO
from app.models import EmployeeSchema, leaves

logger = logging.getLogger(__name__)

def generate_attendance_report():
    """Generates the Excel report for attendance and leave data."""
    try:
        # Attendance data
        attendance_records = EmployeeSchema.query.all()
        data = [{
            'Type': 'Attendance',
            'Employee ID': record.emp_id,
            'Name': record.name,
            'Email': record.email,
            'Department': record.department,
            'Position': record.position,
            'Status/Leave Type': record.status,
            'Date': record.today_date.strftime('%Y-%m-%d'),
            'Time': record.time.strftime('%H:%M:%S'),
            'Latitude': record.latitude,
            'Longitude': record.longitude,
            'Reason': '',
            'Start Date': '',
            'End Date': ''
        } for record in attendance_records]

        # Leave data
        leave_records = leaves.query.all()
        for leave in leave_records:
            data.append({
                'Type': 'Leave',
                'Employee ID': leave.emp_id,
                'Name': '',  # You can join with Employee table if you want name
                'Email': '',
                'Department': '',
                'Position': '',
                'Status/Leave Type': leave.leave_type,
                'Date': '',
                'Time': '',
                'Latitude': '',
                'Longitude': '',
                'Leave Reason': leave.reason,
                'Start Date': leave.start_date.strftime('%Y-%m-%d'),
                'End Date': leave.end_date.strftime('%Y-%m-%d')
            })

        # Convert data to DataFrame
        df = pd.DataFrame(data)

        # Write to BytesIO buffer for in-memory processing
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance')
        output.seek(0)

        return output
    except Exception as e:
        logger.error(f"Attendance report export error: {e}")
        return None
