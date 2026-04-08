// Copyright (c) 2024, Rawas and contributors
// For license information, please see license.txt

frappe.ui.form.on("Medication Error Reporting Form", {
	refresh(frm) {

	},
});

frappe.ui.form.on('Medication Error Reporting Form', {
    refresh: function(frm) {
        // Check if the document is submitted and if the user has the 'System Manager' role
        if (frm.doc.docstatus === 1 && frappe.user_roles.includes('CAPA Approval')) {
            frm.add_custom_button(__('Incident Report Evaluation'), function() {
                // Open the Incident Report Evaluation form and pass the Medication Error Reporting Form ID
                frappe.new_doc('Incident Report Evaluation', {
                    medication_error_reporting_form: frm.doc.name,  // Pass the current form's ID
                    incident_report_form : frm.doc.incident_report_form
                });
            });
        }
    }
});

