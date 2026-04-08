// Copyright (c) 2024, Rawas and contributors
// For license information, please see license.txt

frappe.ui.form.on("Incident Report Form", {
	refresh(frm) {

	},
});

frappe.ui.form.on('Incident Report Form', {
    before_submit: function(frm) {
        if (frm.doc.type_of_incident == "Medication incident") {
            // Create the Medication Error Reporting form and redirect
            frappe.call({
                method: "frappe.client.insert",
                args: {
                    doc: {
                        doctype: "Medication Error Reporting Form",
                        incident_report_form: frm.doc.name  // Link Incident Report Form ID
                    }
                },
                callback: function(response) {
                    if (response.message) {
                        // Open the newly created Medication Error Reporting form
                        frappe.set_route('Form', 'Medication Error Reporting Form', response.message.name);
                    }
                }
            });
        }
    }
});

frappe.ui.form.on('Incident Report Form', {
    refresh: function(frm) {
        // Check if the document is submitted and if the user has the 'System Manager' role
        if (frm.doc.docstatus === 1 && frappe.user_roles.includes('CAPA Approval')) {
            frm.add_custom_button(__('Incident Report Evaluation'), function() {
                // Open the Incident Report Evaluation form and pass the Incident Report Form ID
                frappe.new_doc('Incident Report Evaluation', {
                    incident_report_form: frm.doc.name  // Pass the current form's ID
                });
            });
        }
    }
});
