// Copyright (c) 2024, Rawas and contributors
// For license information, please see license.txt

frappe.listview_settings['Compensatory Off'] = {
    onload: function(listview) {
        listview.page.add_action_item(__('Create Leave Application'), function() {
            let selected = listview.get_checked_items();
            if (selected.length === 0) {
                frappe.msgprint(__('Please select at least one entry'));
                return;
            }

            let promises = selected.map(item => {
                return frappe.db.get_value('Compensatory Off', item.name, 'is_allocated').then(r => {
                    return {
                        name: item.name,
                        is_allocated: r.message.is_allocated
                    };
                });
            });

            Promise.all(promises).then(results => {
                let has_allocated = results.some(item => item.is_allocated);
                if (has_allocated) {
                    frappe.msgprint(__('One or more selected entries have already been allocated and cannot be used to create a new Leave Application.'));
                    return;
                }

                let employees = selected.map(item => item.employee);
                let employee_names = selected.map(item => item.employee_name);
                let from_dates = selected.map(item => item.from_date);
                let to_dates = selected.map(item => item.to_date);
                let over_time_hours = selected.reduce((sum, item) => sum + parseFloat(item.over_time_hours || 0), 0);

                if (new Set(employees).size !== 1) {
                    frappe.msgprint(__('Please select entries for the same employee'));
                    return;
                }

                let dialog = new frappe.ui.Dialog({
                    title: __('Create Leave Application'),
                    fields: [
                        {'fieldname': 'employee', 'fieldtype': 'Data', 'label': 'Employee', 'read_only': 1, 'default': employees[0]},
                        {'fieldname': 'employee_name', 'fieldtype': 'Data', 'label': 'Employee Name', 'read_only': 1, 'default': employee_names[0]},
                        {'fieldname': 'total_hours', 'fieldtype': 'Float', 'label': 'Total Hours', 'read_only': 1, 'default': over_time_hours},
                        {'fieldname': 'from_date', 'fieldtype': 'Date', 'label': 'From Date', 'reqd': 1, 'default': from_dates[0]},
                        {'fieldname': 'to_date', 'fieldtype': 'Date', 'label': 'To Date', 'reqd': 1, 'default': to_dates[to_dates.length - 1]},
                        {'fieldname': 'half_day', 'fieldtype': 'Check', 'label': 'Half Day'},
                        {'fieldname': 'leave_type', 'fieldtype': 'Link', 'label': 'Leave Type', 'reqd': 1, 'options': 'Leave Type', 'default': "Compensatory Off"}
                    ],
                    primary_action: function(values) {
                        frappe.call({
                            method: 'gsh.gsh_kreatao.doctype.compensatory_off.compensatory_off.check_and_create_leave_application',
                            args: {
                                employee: values.employee,
                                from_date: values.from_date,
                                to_date: values.to_date,
                                half_day: values.half_day,
                                leave_type: values.leave_type
                            },
                            callback: function(r) {
                                if (r.message === 'create_allocation') {
                                    frappe.confirm(
                                        __('No Leave Allocation found for this employee and leave type. Do you want to create one?'),
                                        function() {
                                            frappe.call({
                                                method: 'gsh.gsh_kreatao.doctype.compensatory_off.compensatory_off.create_leave_allocation',
                                                args: {
                                                    employee: values.employee,
                                                    from_date: values.from_date,
                                                    to_date: values.to_date,
                                                    leave_type: values.leave_type
                                                },
                                                callback: function(r) {
                                                    if (r.message) {
                                                        update_selected_entries(selected);
                                                        frappe.msgprint(__('Leave Application created successfully'));
                                                        dialog.hide();
                                                    }
                                                }
                                            });
                                        }
                                    );
                                } else if (r.message === 'allocation_updated') {
                                    update_selected_entries(selected);
                                    frappe.msgprint(__('Leave Application created successfully'));
                                    dialog.hide();
                                } else {
                                    update_selected_entries(selected);
                                    frappe.msgprint(__('Leave Application created successfully'));
                                    dialog.hide();
                                }
                            }
                        });
                    },
                    primary_action_label: __('Create')
                });

                dialog.show();
            });
        });
    }
};

function update_selected_entries(selected) {
    selected.forEach(item => {
        frappe.call({
            method: 'frappe.client.set_value',
            args: {
                doctype: 'Compensatory Off',
                name: item.name,
                fieldname: 'is_allocated',
                value: 1
            }
        });
    });
}
