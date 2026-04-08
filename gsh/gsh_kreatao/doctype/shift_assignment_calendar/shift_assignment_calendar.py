# Copyright (c) 2024, Rawas and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ShiftAssignmentCalendar(Document):
	pass

@frappe.whitelist()
def fetch_shift_assignments(department, from_date, to_date):
    shift_assignments = frappe.get_all(
        'Shift Assignment',
        filters={
            'department': department,
            'start_date': ['>=', from_date],
            'end_date': ['<=', to_date],
        },
        fields=['name', 'employee', 'start_date', 'end_date', 'shift_type', 'custom_location', 'employee_name']
    )

    return shift_assignments
