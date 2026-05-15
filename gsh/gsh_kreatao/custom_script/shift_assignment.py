import frappe
from frappe.utils import getdate, nowdate
from datetime import date, timedelta

SHIFT_TYPES_TO_ADD = ["Weekly Off", "NIGHT OFF", "Public Holiday", "On Call Shift", "On Call Day", "On Call Night"]
SHIFT_TYPES_WEEKLY_OFF = ["Weekly Off", "NIGHT OFF", "On Call Shift", "On Call Day", "On Call Night"]
SHIFT_TYPES_TO_REMOVE = ["Weekly Off", "NIGHT OFF", "On Call Shift", "On Call Day", "On Call Night"]


def add_shift_assignment_date_to_holiday_list(doc, method):
    if doc.shift_type not in SHIFT_TYPES_TO_ADD:
        return

    employee = frappe.get_doc("Employee", doc.employee)
    holiday_list_name = employee.holiday_list

    today = getdate(nowdate())
    from_date = date(today.year, 1, 1)
    to_date = date(today.year + 25, 12, 31)

    if not holiday_list_name:
        holiday_list_name = f"{employee.attendance_device_id}:{employee.employee_name}"
        if not frappe.db.exists("Holiday List", holiday_list_name):
            holiday_list = frappe.new_doc("Holiday List")
            holiday_list.holiday_list_name = holiday_list_name
            holiday_list.from_date = from_date
            holiday_list.to_date = to_date
            holiday_list.is_default = 0
            holiday_list.save()
        frappe.db.set_value("Employee", employee.name, "holiday_list", holiday_list_name)

    holiday_list = frappe.get_doc("Holiday List", holiday_list_name)
    existing_dates = {holiday.holiday_date for holiday in holiday_list.holidays}

    start = getdate(doc.start_date)
    end = getdate(doc.end_date or doc.start_date)

    current_date = start
    while current_date <= end:
        if current_date not in existing_dates:
            entry = {
                "holiday_date": current_date,
                "description": f"{doc.shift_type}"
            }
            if doc.shift_type in SHIFT_TYPES_WEEKLY_OFF:
                entry["weekly_off"] = 1
            holiday_list.append("holidays", entry)
        current_date += timedelta(days=1)

    holiday_list.save()


def _create_attendance_if_not_exists(employee, shift_type, att_date):
    exists = frappe.db.exists("Attendance", {
        "employee": employee,
        "attendance_date": att_date,
        "docstatus": ["!=", 2]
    })
    if not exists:
        try:
            att = frappe.get_doc({
                "doctype": "Attendance",
                "employee": employee,
                "attendance_date": att_date,
                "status": "Absent",
                "shift": shift_type
            })
            att.insert(ignore_permissions=True)
            att.submit()
        except Exception as e:
            frappe.log_error(
                f"Attendance creation failed for {employee} on {att_date}: {str(e)}",
                "Shift Assignment"
            )


def _cancel_linked_checkins(employee, att_date):
    """Cancel all Employee Checkins for employee on a given date."""
    checkins = frappe.get_all("Employee Checkin", filters={
        "employee": employee,
        "time": ["between", [
            f"{att_date} 00:00:00",
            f"{att_date} 23:59:59"
        ]],
        "docstatus": 1
    }, pluck="name")

    for checkin in checkins:
        try:
            frappe.get_doc("Employee Checkin", checkin).cancel()
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(
                f"Checkin cancel failed for {employee} on {att_date}: {str(e)}",
                "Shift Assignment Cancel"
            )


def _cancel_linked_attendance(employee, shift_type, att_date):
    """Cancel attendance for employee on a given date."""
    att_name = frappe.db.get_value("Attendance", {
        "employee": employee,
        "attendance_date": att_date,
        "shift": shift_type,
        "docstatus": 1
    })
    if att_name:
        try:
            frappe.get_doc("Attendance", att_name).cancel()
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(
                f"Attendance cancel failed for {employee} on {att_date}: {str(e)}",
                "Shift Assignment Cancel"
            )


def before_cancel_shift_assignment(doc, method):
    """Before cancelling Shift Assignment:
    1. Cancel linked Employee Checkins
    2. Cancel linked Attendance
    So Frappe doesn't block the cancellation.
    """
    if doc.shift_type not in SHIFT_TYPES_TO_REMOVE:
        return

    start_date = getdate(doc.start_date)
    end_date = getdate(doc.end_date or doc.start_date)

    current = start_date
    while current <= end_date:
        _cancel_linked_checkins(doc.employee, current)
        _cancel_linked_attendance(doc.employee, doc.shift_type, current)
        current += timedelta(days=1)


def remove_shift_assignment_dates_from_holiday_list(doc, method):
    """After cancelling Shift Assignment — remove from Holiday List."""
    if doc.shift_type not in SHIFT_TYPES_TO_REMOVE:
        return

    employee = frappe.get_doc("Employee", doc.employee)
    if not employee.holiday_list:
        return

    holiday_list = frappe.get_doc("Holiday List", employee.holiday_list)

    start_date = getdate(doc.start_date)
    end_date = getdate(doc.end_date or doc.start_date)

    dates_to_remove = []
    current_date = start_date
    while current_date <= end_date:
        dates_to_remove.append(current_date)
        current_date += timedelta(days=1)

    holiday_list.holidays = [
        h for h in holiday_list.holidays
        if not (h.holiday_date in dates_to_remove and h.description == doc.shift_type)
    ]
    holiday_list.save()


def update_shift_assignment_dates_in_holiday_list(doc, method):
    if doc.shift_type not in SHIFT_TYPES_TO_REMOVE:
        return

    employee = frappe.get_doc("Employee", doc.employee)
    if not employee.holiday_list:
        return

    holiday_list = frappe.get_doc("Holiday List", employee.holiday_list)

    old_doc = doc.get_doc_before_save()
    if not old_doc:
        return

    old_start = getdate(old_doc.start_date)
    old_end = getdate(old_doc.end_date or old_doc.start_date)
    new_start = getdate(doc.start_date)
    new_end = getdate(doc.end_date or doc.start_date)

    old_dates = set()
    current = old_start
    while current <= old_end:
        old_dates.add(current)
        current += timedelta(days=1)

    new_dates = set()
    current = new_start
    while current <= new_end:
        new_dates.add(current)
        current += timedelta(days=1)

    dates_to_remove = old_dates - new_dates
    if dates_to_remove:
        holiday_list.holidays = [
            h for h in holiday_list.holidays
            if not (h.holiday_date in dates_to_remove and h.description == doc.shift_type)
        ]
        for d in dates_to_remove:
            _cancel_linked_checkins(doc.employee, d)
            _cancel_linked_attendance(doc.employee, doc.shift_type, d)

    existing_dates = {h.holiday_date for h in holiday_list.holidays}
    dates_to_add = new_dates - old_dates
    for d in dates_to_add:
        if d not in existing_dates:
            entry = {
                "holiday_date": d,
                "description": f"{doc.shift_type}"
            }
            if doc.shift_type in SHIFT_TYPES_WEEKLY_OFF:
                entry["weekly_off"] = 1
            holiday_list.append("holidays", entry)

    holiday_list.save()


def _patch_validate_attendance(doc):
    """Patch hrms validate_attendance to ignore already-cancelled attendance."""
    attendances = frappe.get_all(
        "Attendance",
        filters={
            "employee": doc.employee,
            "shift": doc.shift_type,
            "attendance_date": ["between", [doc.start_date, doc.end_date]],
            "docstatus": 1  # only submitted — ignore cancelled
        },
        pluck="name",
    )
    if attendances:
        frappe.throw(
            f"Cannot cancel Shift Assignment: {doc.name} as it is linked to submitted Attendance: {attendances[0]}"
        )


@frappe.whitelist()
def force_cancel_shift_assignment(docname):
    """Cancel Shift Assignment:
    1. Cancel all linked Attendance records first (so hrms validate_attendance passes)
    2. Then cancel Shift Assignment
    3. on_cancel hook removes from Holiday List automatically
    """
    doc = frappe.get_doc("Shift Assignment", docname)

    if doc.docstatus != 1:
        frappe.throw("Shift Assignment is not submitted.")

    start_date = getdate(doc.start_date)
    end_date = getdate(doc.end_date or doc.start_date)

    # Step 1: Cancel ALL attendance for this employee in date range
    # (no shift filter — hrms checks employee + date, not shift)
    current = start_date
    while current <= end_date:
        att_records = frappe.get_all("Attendance", filters={
            "employee": doc.employee,
            "attendance_date": current,
            "docstatus": 1
        }, pluck="name")

        for att_name in att_records:
            try:
                att_doc = frappe.get_doc("Attendance", att_name)
                att_doc.flags.ignore_links = True
                att_doc.cancel()
                frappe.db.commit()
            except Exception as e:
                frappe.log_error(str(e), "Attendance Cancel in force_cancel")

        current += timedelta(days=1)

    # Step 2: Monkey-patch validate_attendance to ignore cancelled records
    import hrms.hr.doctype.shift_assignment.shift_assignment as sa_module
    original_validate = sa_module.ShiftAssignment.validate_attendance
    sa_module.ShiftAssignment.validate_attendance = _patch_validate_attendance

    try:
        doc.flags.ignore_links = True
        doc.cancel()
        frappe.db.commit()
    finally:
        # Always restore original method
        sa_module.ShiftAssignment.validate_attendance = original_validate

    return "Cancelled successfully"
