from __future__ import unicode_literals
import frappe
from frappe import _

def calculate_hours(doc, method):
    if doc.shift in ["On Call Shift", "On Call Day", "On Call Night"]:
        frappe.db.set_value("Attendance", doc.name, 'over_time_hours', doc.working_hours)
    else:

        if doc.working_hours and doc.custom_total_hours:

            working_hours = doc.working_hours
            total_hours = doc.custom_total_hours

            difference = working_hours - total_hours

            if difference >= 0:
                frappe.db.set_value("Attendance", doc.name, 'over_time_hours', float(difference))
                frappe.db.set_value("Attendance", doc.name, 'late_entry_hours', 0.00)
            else:
                frappe.db.set_value("Attendance", doc.name, 'late_entry_hours', float(-difference))
                frappe.db.set_value("Attendance", doc.name, 'over_time_hours', 0.00)


def create_compensatory_leave(doc, method):
    existing_entry = frappe.db.exists('Compensatory Off', {
        'attendance': doc.name
    })
    
    if existing_entry:
        frappe.msgprint(f"A Compensatory Off entry already exists for attendance {doc.name}.")
    else:
        if doc.over_time_hours > 0 and doc.custom_is_compensatory_leave and doc.custom_approved:
            compensatory_leave = frappe.get_doc({
                "doctype": "Compensatory Off",
                "employee": doc.employee,
                "over_time_hours": doc.over_time_hours,
                "attendance": doc.name
            })
            compensatory_leave.insert(ignore_permissions=True)
            frappe.msgprint(f"Compensatory Off created for {doc.employee}.")
