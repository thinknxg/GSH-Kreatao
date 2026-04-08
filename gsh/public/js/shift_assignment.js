frappe.ui.form.on('Shift Assignment', {
    shift_type: function(frm) {
        if (frm.doc.shift_type == 'Public Holiday') {
            frm.set_value('custom_holiday', 1);
        } else {
            frm.set_value('custom_holiday', 0);
        }

        if (frm.doc.shift_type == 'Weekly Off') {
            frm.set_value('custom_weekly_off', 1);
        } else {
            frm.set_value('custom_weekly_off', 0);
        }
    }
});
