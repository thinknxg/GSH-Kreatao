
import frappe
from frappe import _
from frappe.utils import cint, flt, format_datetime, format_duration
from datetime import timedelta, datetime
from frappe.utils import getdate


STATUS_MAP = {
    "Present": "P",
    "Absent": "A",
    "Half Day/Other Half Absent": "HD/A",
    "Half Day/Other Half Present": "HD/P",
    "Half Day": "HD",
    "Work From Home": "WFH",
    "On Leave": "L",
    "Holiday": "H",
    "Holiday On Duty": "H/OD",
    "Weekly Off": "WO",
    "Weekly Off On Duty": "WO/OD",
    "On Duty": "OD",
    "Off Shift": "OS",
    "Off Shift On Duty": "OS/OD",

}

def get_all_dates(from_date, to_date):
    from_date = getdate(from_date)
    to_date = getdate(to_date)

    dates = []
    d = from_date
    while d <= to_date:
        dates.append(d)
        d += timedelta(days=1)
    return dates


def is_on_leave(employee, date):
    return frappe.db.exists(
        "Leave Application",
        {
            "employee": employee,
            "from_date": ["<=", date],
            "to_date": [">=", date],
            "docstatus": 1,
            "status": "Approved",
        }
    )

def is_holiday(date, employee, company):

    emp_holiday_list = frappe.db.get_value("Employee", employee, "holiday_list")

    if emp_holiday_list:
        holiday = frappe.db.get_value(
            "Holiday",
            {"parent": emp_holiday_list, "holiday_date": date},
            ["name", "weekly_off"],
            as_dict=True
        )

        if holiday and not holiday.weekly_off:
            return True

    company_holiday_list = frappe.db.get_value(
        "Company", company, "default_holiday_list"
    )

    if company_holiday_list:
        holiday = frappe.db.get_value(
            "Holiday",
            {"parent": company_holiday_list, "holiday_date": date},
            ["name", "weekly_off"],
            as_dict=True
        )

        if holiday and not holiday.weekly_off:
            return True

    return False

def is_weekly_off(date, employee, company):

    # Employee Holiday List
    emp_holiday_list = frappe.db.get_value(
        "Employee", employee, "holiday_list"
    )

    if emp_holiday_list:
        weekly_off = frappe.db.get_value(
            "Holiday",
            {
                "parent": emp_holiday_list,
                "holiday_date": date
            },
            "weekly_off"
        )

        if weekly_off:
            return True

    # Company Holiday List (fallback)
    company_holiday_list = frappe.db.get_value(
        "Company", company, "default_holiday_list"
    )

    if company_holiday_list:
        weekly_off = frappe.db.get_value(
            "Holiday",
            {
                "parent": company_holiday_list,
                "holiday_date": date
            },
            "weekly_off"
        )

        if weekly_off:
            return True

    return False

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    report_summary = get_report_summary(data)
    return columns, data, None, chart, report_summary

def get_columns():
    return [
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 220,
        },
        {
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "label": _("Employee Name"),
            "width": 0,
            "hidden": 1,
        },
        {
            "label": _("Shift"),
            "fieldname": "shift",
            "fieldtype": "Link",
            "options": "Shift Type",
            "width": 120,
        },
        {
            "label": _("Attendance Date"),
            "fieldname": "attendance_date",
            "fieldtype": "Date",
            "width": 130,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 80,
        },
        {
            "label": _("Shift Start Time"),
            "fieldname": "shift_start",
            "fieldtype": "Data",
            "width": 125,
        },
        {
            "label": _("Shift End Time"),
            "fieldname": "shift_end",
            "fieldtype": "Data",
            "width": 125,
        },
        {
            "label": _("Break Start Time"),
            "fieldname": "break_start",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Break End Time"),
            "fieldname": "break_end",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("In Time"),
            "fieldname": "in_time",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("First Shift End Time"),
            "fieldname": "first_shift_end",
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "label": _("Second Shift Start Time"),
            "fieldname": "second_shift_start",
            "fieldtype": "Data",
            "width": 170,
        },
        {
            "label": _("Out Time"),
            "fieldname": "out_time",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Total Working Hours"),
            "fieldname": "working_hours",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Late Entry By"),
            "fieldname": "late_entry_hrs",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("First Shift Early Exit"),
            "fieldname": "first_shift_early_exit",
            "fieldtype": "Data",
            "width": 170,
        },
        {
            "label": _("Second Shift Late Entry"),
            "fieldname": "second_shift_late_entry",
            "fieldtype": "Data",
            "width": 170,
        },
        {
            "label": _("Early Exit By"),
            "fieldname": "early_exit_hrs",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Department"),
            "fieldname": "department",
            "fieldtype": "Link",
            "options": "Department",
            "width": 150,
        },
        {
            "label": _("Company"),
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 150,
        },
        {
            "label": _("Shift Actual Start Time"),
            "fieldname": "shift_actual_start",
            "fieldtype": "Data",
            "width": 165,
        },
        {
            "label": _("Shift Actual End Time"),
            "fieldname": "shift_actual_end",
            "fieldtype": "Data",
            "width": 165,
        },
        {
            "label": _("Attendance ID"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Attendance",
            "width": 150,
        },
    ]


def has_checkin(employee, date):
    return frappe.db.exists(
        "Employee Checkin",
        {
            "employee": employee,
            "time": ["between", [
                f"{date} 00:00:00",
                f"{date} 23:59:59"
            ]]
        }
    )


def resolve_final_status(entry, date, employee, company):

    is_hol = is_holiday(date, employee, company)
    is_wo = is_weekly_off(date, employee, company)
    on_leave = is_on_leave(employee, date)

    shift_assignments = frappe.get_all(
        "Shift Assignment",
        filters={
            "employee": employee,
            "start_date": ["<=", date],
            "docstatus": 1,
        },
        or_filters=[
            {"end_date": [">=", date]},
            {"end_date": ["is", "not set"]},
        ],
        limit=1,
    )

    shift_exists = True if shift_assignments else False

    full_status = entry.status or ""

    # Half Day
    if full_status == "Half Day":
        if getattr(entry, "half_day_status", None) == "Present":
            full_status = "Half Day/Other Half Present"
        elif getattr(entry, "half_day_status", None) == "Absent":
            full_status = "Half Day/Other Half Absent"

    # Attendance Request Overrides
    if getattr(entry, "reason", None) == "Work From Home":
        full_status = "Work From Home"

    elif getattr(entry, "reason", None) == "On Duty":
        if is_hol:
            full_status = "Holiday On Duty"
        elif is_wo:
            full_status = "Weekly Off On Duty"
        else:
            full_status = "On Duty"

    # No attendance
    if not full_status:

        if on_leave:
            full_status = "On Leave"

        elif is_hol:
            full_status = "Holiday"

        elif is_wo:
            full_status = "Weekly Off"

        elif shift_exists:
            full_status = "Absent"

        else:
            full_status = ""

    # Off Shift
    checkin_exists = has_checkin(employee, date)

    if not shift_exists and checkin_exists:
        if full_status in ("On Duty", "Holiday On Duty", "Weekly Off On Duty"):
            full_status = "Off Shift On Duty"
        else:
            full_status = "Off Shift"

    return STATUS_MAP.get(full_status, "")


# fetch attendance requests for employees within date range
def get_attendance_requests(from_date, to_date, employees):
    return frappe.get_all(
        "Attendance Request",
        filters={
            "employee": ["in", employees],
            "docstatus": 1,
            "from_date": ["<=", to_date],
            "to_date": [">=", from_date],
        },
        fields=[
            "employee",
            "from_date",
            "to_date",
            "reason",
        ],
    )


def get_data(filters):
    # Get existing attendance data
    query = get_query(filters)
    attendance_data = query.run(as_dict=True)

    # Build attendance map (employee + date)
    att_map = {}
    for d in attendance_data:
        att_map.setdefault(d.employee, {})[d.attendance_date] = d

    # Base employee filters
    emp_filters = {"status": "Active"}

    if filters.get("employee"):
        emp_filters["name"] = filters.employee
    
    if filters.get("department"):
        emp_filters["department"] = filters.department

    employees = frappe.get_all(
        "Employee",
        filters=emp_filters,
        fields=["name", "employee_name", "department", "company"]
    )

    employee_names = [e.name for e in employees]

    attendance_requests = get_attendance_requests(
        filters.from_date,
        filters.to_date,
        employee_names
    )

    # Map: employee → date → reason
    ar_map = {}

    for ar in attendance_requests:
        d = getdate(ar.from_date)
        while d <= getdate(ar.to_date):
            ar_map.setdefault(ar.employee, {})[d] = ar.reason
            d += timedelta(days=1)


    # SHIFT TYPE FILTER → FILTER EMPLOYEES ONLY
    if filters.get("shift"):
        eligible_employees = frappe.get_all(
            "Shift Assignment",
            filters={
                "shift_type": filters.shift,
                "start_date": ["<=", filters.to_date],
                "docstatus": 1,
            },
            or_filters=[
                {"end_date": [">=", filters.from_date]},
                {"end_date": ["is", "not set"]},
            ],
            pluck="employee",
            distinct=True,
        )

        employees = [e for e in employees if e.name in eligible_employees]

        if not employees:
            return []

    #  Generate all dates
    dates = get_all_dates(filters.from_date, filters.to_date)

    final_data = []

    for emp in employees:
        for date in dates:
            entry = att_map.get(emp.name, {}).get(date)

            
            # EXISTING ATTENDANCE
            if entry:
                # Inject Attendance Request reason
                entry.reason = ar_map.get(emp.name, {}).get(date)

                entry.status = resolve_final_status(
                    entry=entry,
                    date=date,
                    employee=emp.name,
                    company=emp.company
                )
                final_data.append(entry)
                continue


            # NO ATTENDANCE
            # If shift filter is applied → DO NOT create dummy rows
            if filters.get("shift"):
                continue


            dummy_entry = frappe._dict({
                    "status": "",
                    "reason": ar_map.get(emp.name, {}).get(date)
                })

            status = resolve_final_status(
                entry=dummy_entry,
                date=date,
                employee=emp.name,
                company=emp.company
            )

            final_data.append(
                frappe._dict(
                    {
                        "employee": emp.name,
                        "employee_name": emp.employee_name,
                        "department": emp.department,
                        "company": emp.company,
                        "attendance_date": date,
                        "status": status,
                    }
                )
            )


    # Apply existing calculations
    final_data = update_data(final_data, filters)

    return final_data



def get_attendance_status_for_detailed_view(employee: str, filters, employee_attendance: dict, holidays: list) -> list[dict]:
    # Get all dates from filters
    total_days = get_all_dates(filters.get("from_date"), filters.get("to_date"))
    attendance_values = []

    for shift, status_dict in employee_attendance.items():
        row = {"shift": shift}
        for d in total_days:
            d = getdate(d)
            status_entry = status_dict.get(d, {})
            status = status_entry.get("status") if isinstance(status_entry, dict) else status_entry

            # ---- Half-Day Logic ----
            if status == "Half Day":
                half_day_status = status_entry.get("half_day_status") if isinstance(status_entry, dict) else None
                if half_day_status == "Present":
                    status = "Half Day/Other Half Present"
                elif half_day_status == "Absent":
                    status = "Half Day/Other Half Absent"
                else:
                    status = "Half Day"

            # ---- On Duty / Off Shift ----
            elif status == "On Duty":
                status = "OD"
            elif status == "Off Shift":
                status = "OS"

            # ---- Holiday/Weekly Off ----
            elif not status and holidays:
                status = "H" if d in holidays else ""

            # ---- Map to abbreviation for display ----
            # abbr = STATUS_MAP.get(status, "")
            if status in STATUS_MAP.values():
                abbr = status
            else:
                abbr = STATUS_MAP.get(status, "")

            row[d.strftime("%d-%m-%Y")] = abbr

        attendance_values.append(row)

    return attendance_values


def get_report_summary(data):
    present_records = half_day_records = absent_records = leave_records = od_records = os_records = wfh_records = holiday_records = weekly_off_records = 0
    late_entries = early_exits = 0

    for entry in data:
        st = entry.status
        if st == "P":
            present_records += 1
        elif st == "HD/P":
            half_day_records += 0.5
            present_records += 0.5
        elif st == "HD/A":
            half_day_records += 0.5
            absent_records += 0.5
        elif st == "A":
            absent_records += 1
        elif st == "L":
            leave_records += 1
        elif st == "OD":
            od_records += 1
        elif st == "WFH":
            wfh_records += 1
        elif st == "OS":
            os_records += 1
        elif st == "H":
            holiday_records += 1
        elif st == "WO":
            weekly_off_records += 1

        if getattr(entry, "late_entry", 0):
            late_entries += 1
        if getattr(entry, "early_exit", 0):
            early_exits += 1

    return [
        {"value": present_records, "label": _("Present"), "datatype": "Int", "indicator": "Green"},
        {"value": half_day_records, "label": _("Half Day"), "datatype": "Float", "indicator": "Blue"},
        {"value": absent_records, "label": _("Absent"), "datatype": "Int", "indicator": "Red"},
        {"value": leave_records, "label": _("Leave"), "datatype": "Int", "indicator": "Orange"},
        {"value": od_records, "label": _("On Duty"), "datatype": "Int", "indicator": "#3187D8"},
        {"value": wfh_records, "label": _("Work From Home"), "datatype": "Int", "indicator": "#3187D8"},
        {"value": os_records, "label": _("Off Shift"), "datatype": "Int", "indicator": "#914EE3"},
        # {"value": holiday_records, "label": _("Holiday"), "datatype": "Int", "indicator": "#00B8D9"},
        # {"value": weekly_off_records, "label": _("Weekly Off"), "datatype": "Int", "indicator": "#7E57C2"},
        {"value": late_entries, "label": _("Late Entries"), "datatype": "Int", "indicator": "Red"},
        {"value": early_exits, "label": _("Early Exits"), "datatype": "Int", "indicator": "Red"},
    ]


def get_chart_data(data):
    if not data:
        return None

    total_shift_records = {}
    for entry in data:
        if not entry.shift:
            continue

        total_shift_records.setdefault(entry.shift, 0)
        total_shift_records[entry.shift] += 1

    labels = [_(d) for d in list(total_shift_records)]
    chart = {
        "data": {
            "labels": labels,
            "datasets": [{"name": _("Shift"), "values": list(total_shift_records.values())}],
        },
        "type": "percentage",
    }
    return chart


def get_query(filters):
    attendance = frappe.qb.DocType("Attendance")
    checkin = frappe.qb.DocType("Employee Checkin")
    shift_type = frappe.qb.DocType("Shift Type")

    query = (
        frappe.qb.from_(attendance)
        # .inner_join(checkin)
        # .on(checkin.attendance == attendance.name)
        .left_join(checkin)
        .on(checkin.attendance == attendance.name)

        .left_join(shift_type)
        .on(attendance.shift == shift_type.name)
        .select(
            attendance.name,
            attendance.employee,
            attendance.employee_name,
            attendance.shift,
            attendance.attendance_date,
            attendance.status,
            attendance.in_time,
            attendance.out_time,
            attendance.working_hours,
            attendance.late_entry,
            attendance.early_exit,
            attendance.department,
            attendance.company,
            checkin.shift_start,
            checkin.shift_end,
            checkin.shift_actual_start,
            checkin.shift_actual_end,
            shift_type.enable_late_entry_marking,
            shift_type.late_entry_grace_period,
            shift_type.enable_early_exit_marking,
            shift_type.early_exit_grace_period,
            shift_type.custom_break_start_time.as_("break_start"),
            shift_type.custom_break_end_time.as_("break_end"),
        )
        .where(attendance.docstatus == 1)
        .groupby(attendance.name)
    )

    for filter in filters:
        if filter == "from_date":
            query = query.where(attendance.attendance_date >= filters.from_date)
        elif filter == "to_date":
            query = query.where(attendance.attendance_date <= filters.to_date)
        elif filter == "consider_grace_period":
            continue
        elif filter == "late_entry" and not filters.consider_grace_period:
            query = query.where(attendance.in_time > checkin.shift_start)
        elif filter == "early_exit" and not filters.consider_grace_period:
            query = query.where(attendance.out_time < checkin.shift_end)
        else:
            query = query.where(attendance[filter] == filters[filter])

    return query

def update_data(data, filters):
    for d in data:

        if d.get("shift") and d.get("shift_start") and d.get("shift_end"):

            update_late_entry(d, filters.consider_grace_period)
            update_early_exit(d, filters.consider_grace_period)

            update_first_second_shift(d)
            update_first_second_shift_variances(d)

            d.shift_start, d.shift_end = convert_datetime_to_time_for_same_date(
                d.shift_start, d.shift_end
            )

            d.shift_actual_start, d.shift_actual_end = convert_datetime_to_time_for_same_date(
                d.shift_actual_start, d.shift_actual_end
            )

        d.in_time, d.out_time = format_in_out_time(
            d.in_time, d.out_time, d.attendance_date
        )

        # SAME AS STANDARD ERPNext
        d.working_hours = format_float_precision(d.working_hours)

    return data


def format_float_precision(value):
    precision = cint(frappe.db.get_default("float_precision")) or 2
    return flt(value, precision)


def format_in_out_time(in_time, out_time, attendance_date):
    if in_time and not out_time and in_time.date() == attendance_date:
        in_time = in_time.time()
    elif out_time and not in_time and out_time.date() == attendance_date:
        out_time = out_time.time()
    else:
        in_time, out_time = convert_datetime_to_time_for_same_date(in_time, out_time)
    return in_time, out_time


def convert_datetime_to_time_for_same_date(start, end):
    from datetime import datetime

    def convert(val):
        if not val:
            return None

        if isinstance(val, datetime):
            return val.time()

        if isinstance(val, str):
            try:
                return datetime.strptime(val, "%Y-%m-%d %H:%M:%S").time()
            except:
                try:
                    return datetime.strptime(val, "%d-%m-%Y %H:%M:%S").time()
                except:
                    return None

        return val

    start = convert(start)
    end = convert(end)

    return start, end


def update_late_entry(entry, consider_grace_period):

    entry.late_entry_hrs = None

    if not entry.get("shift_start") or not entry.get("in_time"):
        return

    if consider_grace_period:
        if entry.late_entry:
            grace = entry.late_entry_grace_period if entry.enable_late_entry_marking else 0
            start_time = entry.shift_start + timedelta(minutes=grace)
            diff = entry.in_time - start_time
        else:
            return
    else:
        if entry.in_time > entry.shift_start:
            entry.late_entry = 1
            diff = entry.in_time - entry.shift_start
        else:
            return

    entry.late_entry_hrs = format_duration(diff.total_seconds())


def update_early_exit(entry, consider_grace_period):

    entry.early_exit_hrs = None

    if not entry.get("shift_end") or not entry.get("out_time"):
        return

    if consider_grace_period:
        if entry.early_exit:
            grace = entry.early_exit_grace_period if entry.enable_early_exit_marking else 0
            end_time = entry.shift_end - timedelta(minutes=grace)
            diff = end_time - entry.out_time
        else:
            return
    else:
        if entry.out_time < entry.shift_end:
            entry.early_exit = 1
            diff = entry.shift_end - entry.out_time
        else:
            return

    if diff.total_seconds() > 0:
        entry.early_exit_hrs = format_duration(diff.total_seconds())

# convert timedelta to time
def timedelta_to_time(td):
    if not td:
        return None
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return datetime.strptime(f"{hours:02d}:{minutes:02d}:{seconds:02d}", "%H:%M:%S").time()


# get employee checkins for a given employee and attendance date
def get_employee_checkins(employee, attendance_date):
    return frappe.get_all(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": ["between", [
                f"{attendance_date} 00:00:00",
                f"{attendance_date} 23:59:59"
            ]]
        },
        fields=["time"],
        order_by="time asc"
    )

# helpers to get in and out time for off shift attendance
def get_off_shift_in_out(employee, attendance_date):
    checkins = get_employee_checkins(employee, attendance_date)
    if not checkins:
        return None, None

    in_time = checkins[0].time if checkins else None
    out_time = checkins[-1].time if checkins else None
    return in_time, out_time


def update_first_second_shift(entry):

    # Reset values
    entry.first_shift_end = None
    entry.second_shift_start = None

    if not entry.break_start or not entry.break_end:
        return

    checkins = get_employee_checkins(entry.employee, entry.attendance_date)

    # If only IN and OUT → do nothing
    if not checkins or len(checkins) <= 2:
        return

    break_start = timedelta_to_time(entry.break_start)
    break_end   = timedelta_to_time(entry.break_end)

    # Convert to time list
    checkin_times = [c.time.time() for c in checkins]

    # Remove first (IN) and last (OUT)
    middle_times = checkin_times[1:-1]

    if not middle_times:
        return

    # Helper to calculate nearest time
    def nearest_time(target_time, time_list):
        return min(
            time_list,
            key=lambda t: abs(
                datetime.combine(entry.attendance_date, t) -
                datetime.combine(entry.attendance_date, target_time)
            )
        )

    # First Shift End → nearest to break_start
    entry.first_shift_end = nearest_time(break_start, middle_times)

    # Second Shift Start → nearest to break_end
    entry.second_shift_start = nearest_time(break_end, middle_times)


def update_first_second_shift_variances(entry):

    # Reset values first (important to avoid old data)
    entry.first_shift_early_exit = None
    entry.second_shift_late_entry = None

    if not entry.break_start or not entry.break_end:
        return

    # If shift split not calculated, skip
    if not entry.first_shift_end or not entry.second_shift_start:
        return

    break_start = timedelta_to_time(entry.break_start)
    break_end   = timedelta_to_time(entry.break_end)

    # Convert all to datetime for accurate comparison
    break_start_dt = datetime.combine(entry.attendance_date, break_start)
    break_end_dt   = datetime.combine(entry.attendance_date, break_end)

    first_shift_end_dt = datetime.combine(entry.attendance_date, entry.first_shift_end)
    second_shift_start_dt = datetime.combine(entry.attendance_date, entry.second_shift_start)

    # -------------------------------------------------
    # First Shift Early Exit
    # Only if employee left BEFORE break_start
    # -------------------------------------------------
    if first_shift_end_dt < break_start_dt:
        diff_seconds = (break_start_dt - first_shift_end_dt).total_seconds()
        entry.first_shift_early_exit = format_duration(diff_seconds)

    # -------------------------------------------------
    # Second Shift Late Entry
    # Only if employee returned AFTER break_end
    # -------------------------------------------------
    if second_shift_start_dt > break_end_dt:
        diff_seconds = (second_shift_start_dt - break_end_dt).total_seconds()
        entry.second_shift_late_entry = format_duration(diff_seconds)


