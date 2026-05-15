import frappe
from frappe.utils import getdate
from datetime import date

status_map = {
    "Present": "P",
    "Absent": "A",
    "Half Day/Other Half Absent": "HD/A",
    "Half Day/Other Half Present": "HD/P",
    "Work From Home": "WFH",
    "On Leave": "L",
    "Holiday": "H",
    "Weekly Off": "WO",
    "Night Off": "NO",
}

SHIFT_STATUS_OVERRIDE = {
    "NIGHT OFF": "Night Off",
    "Weekly Off": "Weekly Off",
    "On Call Shift": "Weekly Off",
    "On Call Day": "Weekly Off",
    "On Call Night": "Weekly Off",
    "Public Holiday": "Holiday",
}


def get_holiday_status(holiday_date, holidays):
    if holidays:
        for holiday in holidays:
            if holiday_date == holiday.get("holiday_date"):
                if holiday.get("weekly_off"):
                    if holiday.get("description") == "NIGHT OFF":
                        return "Night Off"
                    return "Weekly Off"
                return "Holiday"
    return None


def get_message():
    colors = ["green", "red", "orange", "#914EE3", "green", "#3187D8", "#878787", "#878787", "#1a1a6e"]
    message = ""
    count = 0
    for status, abbr in status_map.items():
        color = colors[count] if count < len(colors) else "#000"
        message += f"<span style='border-left: 2px solid {color}; padding-right: 12px; padding-left: 5px; margin-right: 3px;'>{frappe._(status)} - {abbr}</span>"
        count += 1
    return message


def get_holiday_map_with_description(filters):
    from hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet import get_date_condition
    holiday_lists = frappe.db.get_all("Holiday List", pluck="name")
    default_holiday_list = frappe.get_cached_value("Company", filters.company, "default_holiday_list")
    holiday_lists.append(default_holiday_list)
    holiday_map = frappe._dict()
    Holiday = frappe.qb.DocType("Holiday")
    holiday_condition = get_date_condition(Holiday.holiday_date, filters)
    for d in holiday_lists:
        if not d:
            continue
        holidays = (
            frappe.qb.from_(Holiday)
            .select(Holiday.holiday_date, Holiday.weekly_off, Holiday.description)
            .where((Holiday.parent == d) & (holiday_condition))
        ).run(as_dict=True)
        holiday_map.setdefault(d, holidays)
    return holiday_map


def execute(filters=None):
    import hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet as mas
    from frappe.utils.nestedset import get_descendants_of
    from hrms.utils import date_diff

    filters = frappe._dict(filters or {})

    if not filters.filter_based_on:
        frappe.throw(frappe._("Please select Filter Based On"))
    if filters.filter_based_on == "Month" and not (filters.month and filters.year):
        frappe.throw(frappe._("Please select month and year."))
    if filters.filter_based_on == "Date Range":
        if not (filters.start_date and filters.end_date):
            frappe.throw(frappe._("Please set the date range."))
        if getdate(filters.start_date) > getdate(filters.end_date):
            frappe.throw(frappe._("Start date cannot be greater than end date."))
        if date_diff(filters.end_date, filters.start_date) > 90:
            frappe.throw(frappe._("Please set a date range less than 90 days."))
    if not filters.company:
        frappe.throw(frappe._("Please select company."))

    filters.companies = [filters.company]
    if filters.include_company_descendants:
        filters.companies.extend(get_descendants_of("Company", filters.company))

    attendance_map = mas.get_attendance_map(filters)
    if not attendance_map:
        frappe.msgprint(frappe._("No attendance records found."), alert=True, indicator="orange")
        return [], [], None, None

    columns = mas.get_columns(filters)
    employee_details, group_by_param_values = mas.get_employee_related_details(filters)
    holiday_map = get_holiday_map_with_description(filters)

    data = []
    default_holiday_list = frappe.get_cached_value("Company", filters.company, "default_holiday_list")

    for employee, details in employee_details.items():
        emp_holiday_list = details.holiday_list or default_holiday_list
        holidays = holiday_map.get(emp_holiday_list)
        employee_attendance = attendance_map.get(employee)
        if not employee_attendance:
            continue

        for shift, status_dict in employee_attendance.items():
            from hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet import get_dates_in_period
            total_days = get_dates_in_period(filters)
            row = {"shift": shift, "employee": employee, "employee_name": details.employee_name}

            for d in total_days:
                d = getdate(d)
                status = status_dict.get(d)

                if status == "Absent" and shift in SHIFT_STATUS_OVERRIDE:
                    status = SHIFT_STATUS_OVERRIDE[shift]
                elif status is None and holidays:
                    holiday_status = get_holiday_status(d, holidays)
                    if holiday_status == "Night Off" and shift == "NIGHT OFF":
                        status = "Night Off"
                    elif holiday_status == "Weekly Off" and shift == "Weekly Off":
                        status = "Weekly Off"
                    elif holiday_status == "Holiday":
                        status = "Holiday"

                abbr = status_map.get(status, "")
                row[d.strftime("%d-%m-%Y")] = abbr

            data.append(row)

    if not data:
        frappe.msgprint(frappe._("No attendance records found for this criteria."), alert=True, indicator="orange")
        return columns, [], None, None

    message = get_message() if not filters.summarized_view else ""
    chart = mas.get_chart_data(attendance_map, filters)
    return columns, data, message, chart
