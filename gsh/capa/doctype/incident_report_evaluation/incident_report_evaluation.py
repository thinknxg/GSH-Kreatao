# Copyright (c) 2024, Rawas and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class IncidentReportEvaluation(Document):
	pass

@frappe.whitelist()
def create_five_whys_analysis_tool(incident_report_evaluation_id):
    # Create a new Five Whys Analysis Tool entry
    new_entry = frappe.get_doc({
        "doctype": "Five Whys Analysis Tool",
        "incident_report_evaluation": incident_report_evaluation_id
    })
    new_entry.insert()
    
    return new_entry.name  # Return the name (ID) of the new entry