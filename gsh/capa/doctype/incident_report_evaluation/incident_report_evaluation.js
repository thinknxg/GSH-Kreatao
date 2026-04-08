// Copyright (c) 2024, Rawas and contributors
// For license information, please see license.txt

frappe.ui.form.on("Incident Report Evaluation", {
	refresh(frm) {

	},
});

// frappe.ui.form.on('Incident Report Evaluation', {
//     on_submit: function(frm) {
//         frappe.call({
//             method: "frappe.client.insert",
//             args: {
//                 doc: {
//                     doctype: "Five Whys Analysis Tool",  // Ensure this is the correct name of your doctype
//                     incident_report_evaluation: frm.doc.name  // Link Incident Report Evaluation ID
//                 }
//             },
//             callback: function(response) {
//                 if (response.message) {
//                     // Redirect to the newly created form
//                     frappe.set_route('Form', 'Five Whys Analysis Tool', response.message.name);
//                 }
//             }
//         });
//     }
// });

// frappe.ui.form.on('Incident Report Evaluation', {
//     before_submit: function(frm) {
//         if (frm.doc.date_of_incident) {
//             // Create the Medication Error Reporting form and redirect
//             frappe.call({
//                 method: "frappe.client.insert",
//                 args: {
//                     doc: {
//                         doctype: "Five Whys Analysis Tool",
//                         incident_report_evaluation: frm.doc.name  // Link Incident Report Evaluation ID
//                     }
//                 },
//                 callback: function(response) {
//                     if (response.message) {
//                         // Open the newly created Medication Error Reporting form
//                         frappe.set_route('Form', 'Five Whys Analysis Tool', response.message.name);
//                     }
//                 }
//             });
//         }
//     }
// });

frappe.ui.form.on('Incident Report Evaluation', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1 && frappe.user_roles.includes('CAPA Approval')) {
            frm.add_custom_button(__('Five Whys Analysis Tool'), function() {
                frappe.new_doc('Five whys Analysis Tool', {
                    incident_report_evaluation: frm.doc.name,
                });
            });
        }
    }
});

frappe.ui.form.on('Incident Report Evaluation', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1 && frappe.user_roles.includes('CAPA Approval')) {
            frm.add_custom_button(__('Fish Bone Analysis'), function() {
                frappe.new_doc('Fish Bone Analysis', {
                    incident_report_evaluation: frm.doc.name,
                });
            });
        }
    }
});