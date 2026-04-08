import frappe
from frappe.utils import today

def mark_attendance_for_shift_assignments():
    shift_types = [
        "Weekly Off", "Public Holiday"
    ]
    
    # Get shift assignments where start_date and end_date match today
    shift_assignments = frappe.get_all(
        "Shift Assignment",
        filters={
            "shift_type": ["in", shift_types],
            "start_date": ["<=", today()],  # start_date should be before or equal to today
            "end_date": [">=", today()],
            "docstatus": 1
        },
        fields=["employee","shift_type"]
    )
    
    for assignment in shift_assignments:
        # Check if attendance already exists for the employee on today's date
        attendance_exists = frappe.get_value(
            "Attendance", {"employee": assignment.employee, "attendance_date": today()}
        )
        
        if not attendance_exists:
            # Create a new attendance record
            attendance = frappe.get_doc({
                "doctype": "Attendance",
                "employee": assignment.employee,
                "attendance_date": today(),
                "status": "Present",
                "shift": assignment.shift_type
            })
            attendance.insert(ignore_permissions=True)
            attendance.submit()
            frappe.db.commit()
            
            frappe.logger().info(f"Marked attendance as Present for Employee: {assignment.employee}")

def schedule_mark_attendance():
    mark_attendance_for_shift_assignments()

def schedule_mark_attendances():
    mark_attendance_for_shift_assignments()

