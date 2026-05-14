import frappe
from frappe.utils import add_days, getdate
from hrms.hr.doctype.shift_assignment_tool.shift_assignment_tool import create_shift_assignment
from gsh.gsh_kreatao.custom_script.shift_assignment import SHIFT_TYPES_TO_ADD, SHIFT_TYPES_WEEKLY_OFF


@frappe.whitelist()
def insert_shift(
    employee: str,
    company: str,
    shift_type: str,
    start_date: str,
    end_date: str | None,
    status: str,
    shift_location: str | None = None,
) -> None:
    filters = {
        "doctype": "Shift Assignment",
        "employee": employee,
        "company": company,
        "shift_type": shift_type,
        "status": status,
        "shift_location": shift_location,
    }
    prev_shift = frappe.db.exists(dict({"end_date": add_days(start_date, -1)}, **filters))
    next_shift = (
        frappe.db.exists(dict({"start_date": add_days(end_date, 1)}, **filters)) if end_date else None
    )

    if prev_shift:
        if next_shift:
            merged_end_date = frappe.db.get_value("Shift Assignment", next_shift, "end_date")
            frappe.db.set_value("Shift Assignment", next_shift, "docstatus", 2)
            frappe.delete_doc("Shift Assignment", next_shift)
        else:
            merged_end_date = end_date or None

        frappe.db.set_value("Shift Assignment", prev_shift, "end_date", merged_end_date)

        # Hook was bypassed — sync holiday list manually for the new date range only
        if shift_type in SHIFT_TYPES_TO_ADD:
            _sync_holiday_for_range(employee, shift_type, start_date, merged_end_date)

    elif next_shift:
        old_start = frappe.db.get_value("Shift Assignment", next_shift, "start_date")
        frappe.db.set_value("Shift Assignment", next_shift, "start_date", start_date)

        # Hook was bypassed — sync holiday list manually for the prepended date range only
        if shift_type in SHIFT_TYPES_TO_ADD:
            _sync_holiday_for_range(employee, shift_type, start_date, add_days(old_start, -1))

    else:
        # Fresh shift — create_shift_assignment calls .submit() which fires on_submit hook normally
        create_shift_assignment(employee, company, shift_type, start_date, end_date, status, shift_location)


def _sync_holiday_for_range(employee, shift_type, start_date, end_date):
    """Directly add holiday entries and attendance records for a date range."""
    from datetime import timedelta

    emp_doc = frappe.get_doc("Employee", employee)
    if not emp_doc.holiday_list:
        return

    holiday_list = frappe.get_doc("Holiday List", emp_doc.holiday_list)
    existing_dates = {h.holiday_date for h in holiday_list.holidays}

    current = getdate(start_date)
    end = getdate(end_date or start_date)

    changed = False
    while current <= end:
        if current not in existing_dates:
            entry = {"holiday_date": current, "description": shift_type}
            if shift_type in SHIFT_TYPES_WEEKLY_OFF:
                entry["weekly_off"] = 1
            holiday_list.append("holidays", entry)
            changed = True

        # Also create attendance record
        _create_attendance_if_not_exists(employee, shift_type, current)
        current += timedelta(days=1)

    if changed:
        holiday_list.save()
        frappe.db.commit()


def _create_attendance_if_not_exists(employee, shift_type, date):
    """Create attendance record if not already exists."""
    exists = frappe.db.exists("Attendance", {
        "employee": employee,
        "attendance_date": date,
        "docstatus": ["!=", 2]
    })
    if not exists:
        try:
            att = frappe.get_doc({
                "doctype": "Attendance",
                "employee": employee,
                "attendance_date": date,
                "status": "Absent",
                "shift": shift_type
            })
            att.insert(ignore_permissions=True)
            att.submit()
        except Exception as e:
            frappe.log_error(
                f"Attendance creation failed for {employee} on {date}: {str(e)}",
                "Roster Override"
            )
