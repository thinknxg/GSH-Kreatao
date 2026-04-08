import frappe
from frappe.utils import getdate

def execute():
    print("updating shift assignments in employee checkin")
    
    employee_checkins = frappe.get_all('Employee Checkin', fields=['name', 'employee', 'time', 'shift'])
    
    for checkin in employee_checkins:
        if not checkin.employee or not checkin.time or not checkin.shift:
            continue

        checkin_date = getdate(checkin.time)
        
        shift_assignment = frappe.db.sql("""
            SELECT name
            FROM `tabShift Assignment`
            WHERE employee = %s
            AND %s BETWEEN start_date AND end_date
            AND shift_type = %s
            LIMIT 1
        """, (checkin.employee, checkin_date, checkin.shift), as_dict=True)
        
        if shift_assignment:
            frappe.db.set_value('Employee Checkin', checkin.name, 'custom_shift_assignment', shift_assignment[0].name)
        else:
            frappe.db.set_value('Employee Checkin', checkin.name, 'custom_shift_assignment', None)
