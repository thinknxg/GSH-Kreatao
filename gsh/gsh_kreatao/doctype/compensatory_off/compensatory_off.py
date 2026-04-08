# Copyright (c) 2024, Rawas and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime
from dateutil.relativedelta import relativedelta

from frappe.model.document import Document


class CompensatoryOff(Document):
	pass



@frappe.whitelist()
def create_leave_application(employee, from_date, to_date, leave_type, half_day):
    leave_application = frappe.get_doc({
        'doctype': 'Leave Application',
        'employee': employee,
        'from_date': from_date,
        'to_date': to_date,
        'leave_type': leave_type,
        'half_day':half_day
    })
    leave_application.insert()
    frappe.db.commit()
    return leave_application.name


@frappe.whitelist()
def check_is_allocated(selected_entries):
    allocated_entries = []
    for entry in selected_entries:
        compensatory_off = frappe.get_doc('Compensatory Off', entry)
        if compensatory_off.is_allocated:
            allocated_entries.append(entry)
    if allocated_entries:
        return ', '.join(allocated_entries)
    return None

@frappe.whitelist()
def check_and_create_leave_application(employee, from_date, to_date, leave_type, half_day):
    allocations = frappe.get_all('Leave Allocation', filters={
        'employee': employee,
        'leave_type': leave_type,
        'from_date': ['<=', to_date],
        'to_date': ['>=', from_date]
    })

    if not allocations:
        return 'create_allocation'
    
    allocation = frappe.get_doc('Leave Allocation', allocations[0].name)
    allocation.new_leaves_allocated = (allocation.new_leaves_allocated or 0) + 1
    allocation.save()
    frappe.db.commit()

    create_leave_application(employee, from_date, to_date, leave_type, half_day)
    return 'allocation_updated'

@frappe.whitelist()
def create_leave_allocation(employee, from_date, to_date, leave_type):
    from_date_dt = datetime.strptime(from_date, '%Y-%m-%d')
    end_of_month = from_date_dt + relativedelta(day=31)

    leave_allocation = frappe.get_doc({
        'doctype': 'Leave Allocation',
        'employee': employee,
        'leave_type': leave_type,
        'from_date': from_date,
        'to_date': end_of_month.strftime('%Y-%m-%d'),
        'new_leaves_allocated': 1
    })
    leave_allocation.insert()
    leave_allocation.submit()
    frappe.db.commit()

    create_leave_application(employee, from_date, to_date, leave_type)
    return leave_allocation.name

@frappe.whitelist()
def create_leave_application_with_allocation_check(selected_entries, employee, from_date, to_date, leave_type):
    allocated_entries = check_is_allocated(selected_entries)
    if allocated_entries:
        frappe.throw(_('Leave application already created for entry: {0}').format(allocated_entries))

    leave_application = frappe.get_doc({
        'doctype': 'Leave Application',
        'employee': employee,
        'from_date': from_date,
        'to_date': to_date,
        'leave_type': leave_type
    })
    leave_application.insert()
    frappe.db.commit()

    for entry in selected_entries:
        compensatory_off = frappe.get_doc('Compensatory Off', entry)
        compensatory_off.is_allocated = 1
        compensatory_off.save()
        frappe.db.commit()

    return leave_application.name