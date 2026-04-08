# Copyright (c) 2025, Rawas and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalaryCertificate(Document):
	pass

@frappe.whitelist()
def get_salary_detail(employee):
    # Get the latest active Salary Structure Assignment for the employee
    salary_structure_assignment = frappe.db.get_value(
        'Salary Structure Assignment',
        {'employee': employee, 'docstatus': 1},
        ['base', 'from_date', 'salary_structure'],
        order_by="from_date desc"
    )
    
    if salary_structure_assignment:
        return {
            "base": salary_structure_assignment[0],
            "from_date": salary_structure_assignment[1],
            "salary_structure": salary_structure_assignment[2]
        }
    else:
        return {}
