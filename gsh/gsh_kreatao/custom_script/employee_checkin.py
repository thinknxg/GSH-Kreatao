import frappe
from frappe.utils import getdate

def fetch_shift_assignment(doc, method):
    if not doc.employee or not doc.time or not doc.shift:
        return

    checkin_date = getdate(doc.time)
    
    shift_assignment = frappe.db.sql("""
        SELECT name
        FROM `tabShift Assignment`
        WHERE employee = %s
        AND %s BETWEEN start_date AND end_date
        AND shift_type = %s
        LIMIT 1
    """, (doc.employee, checkin_date, doc.shift), as_dict=True)

    if shift_assignment:
        doc.custom_shift_assignment = shift_assignment[0].name
    else:
        doc.custom_shift_assignment = None

