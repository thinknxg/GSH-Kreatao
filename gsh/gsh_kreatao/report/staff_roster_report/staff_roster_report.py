import frappe
from frappe import _
from frappe.utils import getdate
import calendar


def execute(filters=None):
    filters = frappe._dict(filters or {})
    validate_filters(filters)
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def validate_filters(filters):
    if not filters.month:
        frappe.throw(_("Please select a Month"))
    if not filters.year:
        frappe.throw(_("Please select a Year"))


def get_columns(filters):
    year = int(filters.year)
    month = int(filters.month)
    month_range = calendar.monthrange(year, month)
    num_days = month_range[1]
    columns = [{"label": _("Employee"), "fieldname": "employee", "fieldtype": "Data", "width": 220}]
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day in range(1, num_days + 1):
        date = getdate("{}-{:02d}-{:02d}".format(year, month, day))
        day_name = day_names[date.weekday()]
        columns.append({"label": "{} {:02d}".format(day_name, day), "fieldname": "day_{}".format(day), "fieldtype": "Data", "width": 100})
    return columns


def get_data(filters):
    year = int(filters.year)
    month = int(filters.month)
    month_range = calendar.monthrange(year, month)
    num_days = month_range[1]
    from_date = getdate("{}-{:02d}-01".format(year, month))
    to_date = getdate("{}-{:02d}-{:02d}".format(year, month, num_days))

    emp_filters = {"status": "Active"}
    if filters.company:
        emp_filters["company"] = filters.company
    if filters.department:
        emp_filters["department"] = filters.department
    if filters.employee:
        emp_filters["name"] = filters.employee

    employees = frappe.get_all(
        "Employee",
        filters=emp_filters,
        fields=["name", "employee_name", "date_of_joining", "relieving_date", "holiday_list"],
        order_by="employee_name asc",
    )
    if not employees:
        return []

    emp_names = [e.name for e in employees]

    attendance_records = frappe.db.sql(
        "SELECT employee, attendance_date, status FROM `tabAttendance` WHERE attendance_date BETWEEN %(from_date)s AND %(to_date)s AND employee IN %(employees)s AND docstatus = 1",
        {"employees": emp_names, "from_date": from_date, "to_date": to_date},
        as_dict=1,
    )
    att_map = {}
    for row in attendance_records:
        att_map.setdefault(row.employee, {})[row.attendance_date] = row

    shift_assignments = frappe.db.sql(
        "SELECT employee, shift_type, start_date, end_date, custom_weekly_off, custom_holiday FROM `tabShift Assignment` WHERE docstatus = 1 AND status = 'Active' AND start_date <= %(to_date)s AND (end_date >= %(from_date)s OR end_date IS NULL) AND employee IN %(employees)s",
        {"employees": emp_names, "from_date": from_date, "to_date": to_date},
        as_dict=1,
    )
    shift_map = {}
    for sa in shift_assignments:
        shift_map.setdefault(sa.employee, []).append(sa)

    holiday_lists = list(set(e.holiday_list for e in employees if e.holiday_list))
    holiday_map = {}
    if holiday_lists:
        holidays = frappe.db.sql(
            "SELECT parent, holiday_date, description FROM `tabHoliday` WHERE parent IN %(lists)s AND holiday_date BETWEEN %(from_date)s AND %(to_date)s",
            {"lists": holiday_lists, "from_date": from_date, "to_date": to_date},
            as_dict=1,
        )
        for h in holidays:
            holiday_map.setdefault(h.parent, {})[h.holiday_date] = h.description

    data = []
    for emp in employees:
        row = {"employee": "{} ({})".format(emp.employee_name, emp.name)}
        emp_holidays = holiday_map.get(emp.holiday_list, {})
        emp_att = att_map.get(emp.name, {})
        emp_shifts = shift_map.get(emp.name, [])

        for day in range(1, num_days + 1):
            date = getdate("{}-{:02d}-{:02d}".format(year, month, day))
            fieldname = "day_{}".format(day)
            doj = getdate(emp.date_of_joining) if emp.date_of_joining else None
            relieving = getdate(emp.relieving_date) if emp.relieving_date else None

            if (doj and date < doj) or (relieving and date > relieving):
                row[fieldname] = "NA"
                continue

            att = emp_att.get(date)
            if att:
                status = att.status
                if status == "Present":
                    row[fieldname] = "P"
                elif status == "Absent":
                    row[fieldname] = "A"
                elif status == "Half Day":
                    row[fieldname] = "H/D"
                elif status == "On Leave":
                    row[fieldname] = "OL"
                elif status == "Work From Home":
                    row[fieldname] = "WFH"
                else:
                    row[fieldname] = status
                continue

            shift_for_day = get_shift_for_date(emp_shifts, date)
            if shift_for_day:
                st = shift_for_day.shift_type or ""
                if shift_for_day.custom_weekly_off or st.lower() == "weekly off":
                    row[fieldname] = "WO"
                elif shift_for_day.custom_holiday:
                    row[fieldname] = "H"
                elif "STRN" in st.upper():
                    row[fieldname] = "NO"
                else:
                    row[fieldname] = "UM"
                continue

            if date in emp_holidays:
                desc = emp_holidays[date] or ""
                if "weekly off" in desc.lower():
                    row[fieldname] = "WO"
                else:
                    row[fieldname] = "H"
                continue

            row[fieldname] = "UM"

        data.append(row)
    return data


def get_shift_for_date(shifts, date):
    for sa in shifts:
        start = getdate(sa.start_date)
        end = getdate(sa.end_date) if sa.end_date else None
        if start <= date and (end is None or date <= end):
            return sa
    return None
