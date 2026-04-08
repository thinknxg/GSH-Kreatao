import frappe
from frappe.utils import getdate, nowdate
from datetime import date, timedelta

SHIFT_TYPES_TO_ADD = ["Weekly Off", "Public Holiday", "On Call Shift", "On Call Day", "On Call Night"]
SHIFT_TYPES_WEEKLY_OFF = ["Weekly Off", "On Call Shift", "On Call Day", "On Call Night"]

def add_shift_assignment_date_to_holiday_list(doc, method):
    if doc.shift_type not in SHIFT_TYPES_TO_ADD:
        return

    employee = frappe.get_doc("Employee", doc.employee)
    holiday_list_name = employee.holiday_list

    today = getdate(nowdate())
    from_date = date(today.year, 1, 1)
    to_date = date(today.year + 25, 12, 31)

    # Create holiday list if not set
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

    # Load holiday list
    holiday_list = frappe.get_doc("Holiday List", holiday_list_name)

    # # Adjust from_date / to_date if needed
    # if doc.start_date < holiday_list.from_date:
    #     holiday_list.from_date = doc.start_date
    # if doc.end_date and doc.end_date > holiday_list.to_date:
    #     holiday_list.to_date = doc.end_date

    # Prepare existing holiday dates for quick lookup
    existing_dates = {holiday.holiday_date for holiday in holiday_list.holidays}

    # Iterate from start_date to end_date (inclusive)
    start = doc.start_date
    end = doc.end_date or doc.start_date  # fallback to start_date if end_date is None

    current_date = start
    current_date = getdate(current_date)
    end = getdate(end)
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

    # Save only once after all additions
    holiday_list.save()


SHIFT_TYPES_TO_REMOVE = ["Weekly Off","On Call Shift", "On Call Day", "On Call Night"]

def remove_shift_assignment_dates_from_holiday_list(doc, method):
    if doc.shift_type not in SHIFT_TYPES_TO_REMOVE:
        return

    employee = frappe.get_doc("Employee", doc.employee)
    if not employee.holiday_list:
        return

    # Load the holiday list
    holiday_list = frappe.get_doc("Holiday List", employee.holiday_list)

    # Track dates to remove
    start_date = doc.start_date
    end_date = doc.end_date or doc.start_date

    # Collect dates in the range
    dates_to_remove = []
    current_date = start_date
    current_date = getdate(current_date)
    end_date = getdate(end_date)
    while current_date <= end_date:
        dates_to_remove.append(current_date)
        current_date += timedelta(days=1)

    # Filter and keep holidays that do NOT match the current shift assignment
    holiday_list.holidays = [
        h for h in holiday_list.holidays
        if not (h.holiday_date in dates_to_remove and h.description == doc.shift_type)
    ]

    holiday_list.save()

def update_shift_assignment_dates_in_holiday_list(doc, method):
    if doc.shift_type not in SHIFT_TYPES_TO_REMOVE:  # only process these shift types
        return

    employee = frappe.get_doc("Employee", doc.employee)
    if not employee.holiday_list:
        return

    holiday_list = frappe.get_doc("Holiday List", employee.holiday_list)

    # Fetch the old doc values (before update)
    old_doc = doc.get_doc_before_save()
    if not old_doc:
        return  # nothing to compare if first save

    old_start = getdate(old_doc.start_date)
    old_end = getdate(old_doc.end_date or old_doc.start_date)
    new_start = getdate(doc.start_date)
    new_end = getdate(doc.end_date or doc.start_date)

    # --------------------------
    # 1. Handle removed dates
    # --------------------------
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

    dates_to_remove = old_dates - new_dates  # existed before, but not now
    if dates_to_remove:
        holiday_list.holidays = [
            h for h in holiday_list.holidays
            if not (h.holiday_date in dates_to_remove and h.description == doc.shift_type)
        ]

    # --------------------------
    # 2. Handle added dates
    # --------------------------
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

    # Save updates
    holiday_list.save()