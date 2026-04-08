import frappe
from frappe import _

def execute():
    print("updating attendance hours")
    attendance_entries = frappe.get_all(
        'Attendance', 
        filters={
            'status': 'Present',
            'late_entry_hours': ['=', 0],
            'over_time_hours': ['=', 0]
        },
        fields=['name', 'working_hours', 'custom_total_hours']
    )

    for entry in attendance_entries:
        doc = frappe.get_doc('Attendance', entry['name'])
        if doc.working_hours and doc.custom_total_hours:
            working_hours = doc.working_hours
            total_hours = doc.custom_total_hours
            difference = working_hours - total_hours

            if difference >= 0:
                doc.over_time_hours = float(difference)
                doc.late_entry_hours = 0.00
            else:
                doc.late_entry_hours = float(-difference)
                doc.over_time_hours = 0.00
            
            doc.save()
            frappe.db.commit()
