frappe.ui.form.on('Attendance Request', {
    refresh: function(frm) {
        frm.add_custom_button(__('Get Overtime Hours'), function() {
            calculate_overtime_hours(frm);
        });
    }
});

function calculate_overtime_hours(frm) {
    let start_date = frm.doc.from_date;
    let end_date = frm.doc.to_date;
    let employee = frm.doc.employee;

    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Attendance',
            filters: {
                employee: employee,
                attendance_date: ['between', [start_date, end_date]],
                custom_is_compensatory_leave: 1,
                custom_approved: 1
            },
            fields: ['over_time_hours']
        },
        callback: function(response) {
            let attendances = response.message;
            let total_overtime = 0;

            attendances.forEach(function(attendance) {
                total_overtime += attendance.over_time_hours;
            });

            frm.set_value('custom_overtime_hours', total_overtime);
            frm.refresh_field('custom_overtime_hours');
        }
    });
}
