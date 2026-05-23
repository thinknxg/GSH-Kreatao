import frappe
from frappe.utils import getdate
from datetime import timedelta

def execute():
    shifts = frappe.get_all("Shift Assignment",
        filters={"shift_type": ["in", ["On Call Shift", "On Call Day", "On Call Night"]], "docstatus": 1},
        fields=["name", "employee", "shift_type", "start_date", "end_date"]
    )
    print("Total shift assignments:", len(shifts))
    created = 0
    for s in shifts:
        start = getdate(s.start_date)
        end = getdate(s.end_date or s.start_date)
        current = start
        while current <= end:
            exists = frappe.db.exists("Attendance", {"employee": s.employee, "attendance_date": current, "docstatus": ["!=", 2]})
            if not exists:
                try:
                    att = frappe.get_doc({"doctype": "Attendance", "employee": s.employee, "attendance_date": current, "status": "Absent", "shift": s.shift_type})
                    att.insert(ignore_permissions=True)
                    att.submit()
                    frappe.db.commit()
                    created += 1
                except Exception as e:
                    print(f"Error: {s.employee} {current} {str(e)}")
            current += timedelta(days=1)
    print(f"Done! Created {created} attendance records")
