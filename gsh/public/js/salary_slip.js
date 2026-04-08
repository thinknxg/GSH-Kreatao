// frappe.ui.form.on('Salary Slip', {
//     refresh: function(frm) {
//         frm.add_custom_button(__('Get Overtime and Late Entry'), function() {
//             calculate_overtime_and_late_entry(frm);
//         });
//     }
// });

// function calculate_overtime_and_late_entry(frm) {
//     let start_date = frm.doc.start_date;
//     let end_date = frm.doc.end_date;
//     let employee = frm.doc.employee;

//     let total_overtime = 0;
//     let total_late_entry = 0;

//     let overtimePromise = frappe.call({
//         method: 'frappe.client.get_list',
//         args: {
//             doctype: 'Attendance',
//             filters: {
//                 employee: employee,
//                 attendance_date: ['between', [start_date, end_date]],
//                 custom_is_paid: 1,
//                 custom_approved: 1,
//                 over_time_hours: ['>', 0]
//             },
//             fields: ['over_time_hours']
//         }
//     }).then(function(response) {
//         let attendances = response.message;

//         let promises = attendances.map(function(attendance) {
//             return frappe.call({
//                 method: 'frappe.client.get_value',
//                 args: {
//                     doctype: 'Employee',
//                     filters: { name: employee },
//                     fieldname: 'custom_over_time_rate'
//                 }
//             }).then(function(res) {
//                 let over_time_rate = res.message.custom_over_time_rate || 0;
//                 total_overtime += (attendance.over_time_hours * over_time_rate);
//             });
//         });

//         return Promise.all(promises);
//     });

//     let lateEntryPromise = frappe.call({
//         method: 'frappe.client.get_list',
//         args: {
//             doctype: 'Attendance',
//             filters: {
//                 employee: employee,
//                 attendance_date: ['between', [start_date, end_date]],
//                 late_entry_hours: ['>', 0]
//             },
//             fields: ['late_entry_hours']
//         }
//     }).then(function(response) {
//         let attendances = response.message;

//         let promises = attendances.map(function(attendance) {
//             return frappe.call({
//                 method: 'frappe.client.get_value',
//                 args: {
//                     doctype: 'Employee',
//                     filters: { name: employee },
//                     fieldname: 'custom_late_entry_rate'
//                 }
//             }).then(function(res) {
//                 let late_entry_rate = res.message.custom_late_entry_rate || 0;
//                 total_late_entry += (attendance.late_entry_hours * late_entry_rate);
//             });
//         });

//         return Promise.all(promises);
//     });

//     Promise.all([overtimePromise, lateEntryPromise]).then(function() {
//         let overtime_exists = frm.doc.earnings.some(e => e.salary_component === 'Overtime');
//         let late_entry_exists = frm.doc.deductions.some(d => d.salary_component === 'Late Hours');

//         if (overtime_exists) {
//             frm.doc.earnings.forEach(e => {
//                 if (e.salary_component === 'Overtime') {
//                     e.amount = total_overtime;
//                 }
//             });
//         } else {
//             frm.add_child('earnings', {
//                 salary_component: 'Overtime',
//                 amount: total_overtime
//             });
//         }

//         if (late_entry_exists) {
//             frm.doc.deductions.forEach(d => {
//                 if (d.salary_component === 'Late Hours') {
//                     d.amount = total_late_entry;
//                 }
//             });
//         } else {
//             frm.add_child('deductions', {
//                 salary_component: 'Late Hours',
//                 amount: total_late_entry
//             });
//         }

//         frm.refresh_field('earnings');
//         frm.refresh_field('deductions');
//     });
// }
frappe.ui.form.on('Salary Slip', {
    refresh: function(frm) {
        frm.add_custom_button(__('Get Overtime and Late Entry'), function() {
            calculate_overtime_and_late_entry(frm);
        });
    }
});

function calculate_overtime_and_late_entry(frm) {
    let start_date = frm.doc.start_date;
    let end_date = frm.doc.end_date;
    let employee = frm.doc.employee;

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
                        console.log("Overtime Rate:", over_time_rate);
                        total_overtime += (attendance.over_time_hours * over_time_rate);
                        console.log("Total Overtime:", total_overtime);
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
                        console.log("Late Entry Rate:", late_entry_rate);
                        total_late_entry += (attendance.late_entry_hours * late_entry_rate);
                        console.log("Total Late Entry:", total_late_entry);
                    });
                }
                return Promise.resolve();
            });

            Promise.all(promises).then(function() {
                console.log("Final Total Overtime:", total_overtime);
                console.log("Final Total Late Entry:", total_late_entry);

                let overtime_exists = frm.doc.earnings.some(e => e.salary_component === 'Overtime');
                let late_entry_exists = frm.doc.deductions.some(d => d.salary_component === 'Late Hours');

                if (overtime_exists) {
                    frm.doc.earnings.forEach(e => {
                        if (e.salary_component === 'Overtime') {
                            e.amount = total_overtime;
                        }
                    });
                } else {
                    frm.add_child('earnings', {
                        salary_component: 'Overtime',
                        amount: total_overtime
                    });
                }

                if (late_entry_exists) {
                    frm.doc.deductions.forEach(d => {
                        if (d.salary_component === 'Late Hours') {
                            d.amount = total_late_entry;
                        }
                    });
                } else {
                    frm.add_child('deductions', {
                        salary_component: 'Late Hours',
                        amount: total_late_entry
                    });
                }

                frm.refresh_field('earnings');
                frm.refresh_field('deductions');
            });
        }
    });
}

frappe.ui.form.on('Salary Slip', {
    before_save: function(frm) {
        frm.trigger('calculate_saturday_allowance_deduction');
    },
    before_insert: function(frm) {
        frm.trigger('calculate_saturday_allowance_deduction');
    },
    on_submit: function(frm) {
        frm.trigger('calculate_saturday_allowance_deduction');
    },
    calculate_saturday_allowance_deduction: function(frm) {
        if (frm.doc.start_date && frm.doc.end_date && frm.doc.employee) {
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Attendance',
                    filters: {
                        employee: frm.doc.employee,
                        status: 'On Leave',
                        docstatus: 1,
                        leave_type: ['in', ['Annual Leave', 'Maternity Leave', 'Haj Leave', 'Marriage Leave', 'Parental Leave(Male Staff Only)',
                        'Widow Muslim Leave(Omani Female)', 'Widow Non Muslim leave(Female Non Omani)']],
                        attendance_date: ['between', [frm.doc.start_date, frm.doc.end_date]]
                    },
                    fields: ['name'],
                    limit_page_length: 1000
                },
                callback: function(r) {
                    if (r.message) {
                        let leave_days = r.message.length;
                        console.log("Leave Days: ", leave_days);

                        let overtime_allowance = frm.doc.earnings.find(row => row.salary_component === 'Saturday Fixed Overtime Allowance');
                        if (overtime_allowance) {
                            let default_amount = overtime_allowance.default_amount;
                            console.log("Default Amount: ", default_amount);

                            let per_day_amount = default_amount / frm.doc.total_working_days;
                            console.log("Per Day Amount: ", per_day_amount);

                            let deduction_amount = per_day_amount * leave_days;
                            console.log("Deduction Amount: ", deduction_amount);

                            let deduction_component = frm.doc.deductions.find(row => row.salary_component === 'Saturday Allowance Deduction');
                            if (!deduction_component) {
                                let new_row = frm.add_child('deductions');
                                new_row.salary_component = 'Saturday Allowance Deduction';
                                new_row.amount = deduction_amount;
                                console.log("New Deduction Added: ", deduction_amount);
                            } else {
                                deduction_component.amount = deduction_amount;
                                console.log("Deduction Updated: ", deduction_amount);
                            }
                            frm.refresh_field('deductions');
                        } else {
                            console.log("Saturday Fixed Overtime Allowance not found in earnings.");
                        }
                    } else {
                        console.log("No matching leave days found.");
                    }
                }
            });
        } else {
            console.log("Required fields (start_date, end_date, employee) are missing.");
        }
    }
});
