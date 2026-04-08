// Copyright (c) 2024, Rawas and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Shift Assignment Calendar", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Shift Assignment Calendar', {
    fetch_shift_assignment: function(frm) {
        if (!frm.doc.department || !frm.doc.from_date || !frm.doc.to_date) {
            frappe.msgprint(__('Please select Department, From Date, and To Date.'));
            return;
        }
        
        frappe.call({
            method: 'gsh.gsh_kreatao.doctype.shift_assignment_calendar.shift_assignment_calendar.fetch_shift_assignments',
            args: {
                department: frm.doc.department,
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date
            },
            callback: function(r) {
                if (r.message) {
                    frm.clear_table('shift_assignment_calendar_table');
                    $.each(r.message, function(i, d) {
                        let row = frm.add_child('shift_assignment_calendar_table');
                        row.shift_assignment = d.name;
                        row.employee = d.employee;
                        row.employee_name = d.employee_name;
                        row.start_date = d.start_date;
                        row.end_date = d.end_date;
                        row.shift_type = d.shift_type;
                        row.location = d.custom_location;
                    });
                    frm.refresh_field('shift_assignment_calendar_table');
                }
            }
        });
    }
});

frappe.ui.form.on('Shift Assignment Calendar', {
    from_date: function(frm) {
        if (frm.doc.from_date) {
            let from_date = frappe.datetime.str_to_obj(frm.doc.from_date);

            let to_date = frappe.datetime.add_days(from_date, 7);

            let formatted_to_date = frappe.datetime.obj_to_str(to_date);

            frm.set_value('to_date', formatted_to_date);
        }
    }
});
