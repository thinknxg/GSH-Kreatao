frappe.ui.form.on('Payroll Entry', {
    refresh: function(frm) {
        frm.add_custom_button(__('Get Overtime and Late Entry'), function() {
            get_overtime_and_late_entry_for_all_salary_slips(frm);
        });
    }
});

function get_overtime_and_late_entry_for_all_salary_slips(frm) {
    let payroll_entry = frm.doc.name;

    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Salary Slip',
            filters: {
                payroll_entry: payroll_entry,
                docstatus: 0
            },
            fields: ['name', 'employee', 'start_date', 'end_date']
        },
        callback: function(response) {
            let salary_slips = response.message;

            let promises = salary_slips.map(function(slip) {
                return calculate_overtime_and_late_entry(slip);
            });

            Promise.all(promises).then(function() {
                frappe.msgprint(__('Overtime and Late Entry amounts have been updated for all salary slips.'));
                frm.reload_doc();
            });
        }
    });
}

function calculate_overtime_and_late_entry(slip) {
    return new Promise(function(resolve, reject) {
        let { start_date, end_date, employee, name: salary_slip_name } = slip;

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Attendance',
                filters: {
                    employee: employee,
                    attendance_date: ['between', [start_date, end_date]],
                    docstatus: 1,
                    custom_is_paid: 1,
                    custom_approved: 1
                },
                fields: ['over_time_hours', 'late_entry_hours']
            },
            callback: function(response) {
                let attendances = response.message;
                let total_overtime = 0;
                let total_late_entry = 0;

                let promises = attendances.map(function(attendance) {
                    if (attendance.over_time_hours > 0 && attendance.late_entry_hours === 0) {
                        return frappe.call({
                            method: 'frappe.client.get_value',
                            args: {
                                doctype: 'Employee',
                                filters: { name: employee },
                                fieldname: 'custom_over_time_rate'
                            }
                        }).then(function(res) {
                            let over_time_rate = res.message.custom_over_time_rate || 0;
                            total_overtime += (attendance.over_time_hours * over_time_rate);
                        });
                    } else if (attendance.late_entry_hours > 0 && attendance.over_time_hours === 0) {
                        return frappe.call({
                            method: 'frappe.client.get_value',
                            args: {
                                doctype: 'Employee',
                                filters: { name: employee },
                                fieldname: 'custom_late_entry_rate'
                            }
                        }).then(function(res) {
                            let late_entry_rate = res.message.custom_late_entry_rate || 0;
                            total_late_entry += (attendance.late_entry_hours * late_entry_rate);
                        });
                    }
                    return Promise.resolve();
                });

                Promise.all(promises).then(function() {
                    frappe.call({
                        method: 'frappe.client.get',
                        args: {
                            doctype: 'Salary Slip',
                            name: salary_slip_name
                        },
                        callback: function(r) {
                            let salary_slip = r.message;
                            let earnings = salary_slip.earnings || [];
                            let deductions = salary_slip.deductions || [];

                            let overtime_entry = earnings.find(e => e.salary_component === 'Overtime');
                            if (overtime_entry) {
                                overtime_entry.amount = total_overtime;
                            } else {
                                earnings.push({
                                    salary_component: 'Overtime',
                                    amount: total_overtime
                                });
                            }

                            let late_hours_entry = deductions.find(d => d.salary_component === 'Late Hours');
                            if (late_hours_entry) {
                                late_hours_entry.amount = total_late_entry;
                            } else {
                                deductions.push({
                                    salary_component: 'Late Hours',
                                    amount: total_late_entry
                                });
                            }

                            frappe.call({
                                method: 'frappe.client.set_value',
                                args: {
                                    doctype: 'Salary Slip',
                                    name: salary_slip_name,
                                    fieldname: {
                                        earnings: earnings,
                                        deductions: deductions
                                    }
                                },
                                callback: function() {
                                    resolve();
                                }
                            });
                        }
                    });
                });
            }
        });
    });
}


frappe.ui.form.on('Payroll Entry', {
    refresh: function(frm) {

        frm.add_custom_button(__('Calculate Saturday Allowance Deduction'), function() {
        // frm.add_custom_button(__('Get Overtime Allowance Deduction'), function() {

            calculate_saturday_allowance_for_all_salary_slips(frm);
        });
    }
});

function calculate_saturday_allowance_for_all_salary_slips(frm) {
    let payroll_entry = frm.doc.name;

    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Salary Slip',
            filters: {
                payroll_entry: payroll_entry,
                docstatus: 0
            },
            fields: ['name', 'employee', 'start_date', 'end_date'],
            limit_page_length: 1000 
        },
        callback: function(response) {
            let salary_slips = response.message;
            console.log("Total Employees: ", response.message.length);

            process_salary_slips_sequentially(salary_slips, 0, frm);
        }
    });
}

function process_salary_slips_sequentially(salary_slips, index, frm) {
    if (index < salary_slips.length) {
        calculate_saturday_allowance_deduction(salary_slips[index]).then(function() {
            process_salary_slips_sequentially(salary_slips, index + 1, frm);
        });
    } else {

        frappe.msgprint(__('Saturday Allowance Deduction has been updated for all salary slips.'));
        // frappe.msgprint(__('Overtime Deduction has been updated for all salary slips.'));

        frm.reload_doc();
    }
}

function calculate_saturday_allowance_deduction(slip) {
    return new Promise(function(resolve, reject) {
        let start_date = slip.start_date;
        let end_date = slip.end_date;
        let employee = slip.employee;
        let salary_slip_name = slip.name;

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Attendance',
                filters: {
                    employee: employee,
                    attendance_date: ['between', [start_date, end_date]],
                    status: 'On Leave',
                    docstatus: 1,
                    leave_type: ['in', ['Annual Leave', 'Maternity Leave', 'Haj Leave', 'Marriage Leave', 'Parental Leave(Male Staff Only)',
                    'Widow Muslim Leave(Omani Female)', 'Widow Non Muslim leave(Female Non Omani)']]
                },
                fields: ['name'],
                limit_page_length: 1000
            }
        }).then(function(response) {
            let leave_days = response.message.length;

            if (leave_days > 0) {
                frappe.call({
                    method: 'frappe.client.get',
                    args: {
                        doctype: 'Salary Slip',
                        name: salary_slip_name
                    },
                    callback: function(r) {
                        let salary_slip = r.message;
                        let earnings = salary_slip.earnings || [];
                        let deductions = salary_slip.deductions || [];
                        let total_working_days = salary_slip.total_working_days;

                        let overtime_allowance = earnings.find(e => e.salary_component === 'Saturday Fixed Overtime Allowance');
                        // let overtime_allowance = earnings.find(e => e.salary_component === 'Overtime');

                        if (overtime_allowance) {
                            let per_day_amount = overtime_allowance.default_amount / total_working_days;
                            let deduction_amount = per_day_amount * leave_days;

                            let deduction_entry = deductions.find(d => d.salary_component === 'Saturday Allowance Deduction');
                            // let deduction_entry = deductions.find(d => d.salary_component === 'Overtime Allowance Deduction');

                            if (deduction_entry) {
                                deduction_entry.amount = deduction_amount;
                            } else {
                                deductions.push({

                                    salary_component: 'Saturday Allowance Deduction',
                                    // salary_component: 'Overtime Allowance Deduction',
                                    amount: deduction_amount
                                });
                            }

                            frappe.call({
                                method: 'frappe.client.set_value',
                                args: {
                                    doctype: 'Salary Slip',
                                    name: salary_slip_name,
                                    fieldname: {
                                        deductions: deductions
                                    }
                                },
                                callback: function() {
                                    resolve();
                                }
                            });
                        } else {
                            resolve();
                        }
                    }
                });
            } else {
                resolve();
            }
        });
    });
}
