
from datetime import timedelta

import frappe
from frappe import _
from frappe.query_builder import Criterion
from frappe.utils import cint, flt, format_datetime, format_duration
from datetime import timedelta, datetime
from frappe.utils import getdate


# from erpnext.accounts.utils import build_qb_match_conditions


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


def get_data(filters):
    data = get_attendance_with_checkins(filters)
    data = update_data(data, filters)
    if filters.include_attendance_without_checkins:
        data.extend(get_attendance_without_checkins(filters))
    return data


def get_report_summary(data):
    if not data:
        return None

    present_records = half_day_records = absent_records = late_entries = early_exits = 0

    for entry in data:
        if entry.status == "Present":
            present_records += 1
        elif entry.status == "Half Day":
            half_day_records += 1
        else:
            absent_records += 1

        if getattr(entry, "late_entry", False):
            late_entries += 1
        if getattr(entry, "early_exit", False):
            early_exits += 1

    return [
        {"value": present_records, "indicator": "Green", "label": _("Present Records"), "datatype": "Int"},
        {"value": half_day_records, "indicator": "Blue", "label": _("Half Day Records"), "datatype": "Int"},
        {"value": absent_records, "indicator": "Red", "label": _("Absent Records"), "datatype": "Int"},
        {"value": late_entries, "indicator": "Red", "label": _("Late Entries"), "datatype": "Int"},
        {"value": early_exits, "indicator": "Red", "label": _("Early Exits"), "datatype": "Int"},
    ]


def get_chart_data(data):
    if not data:
        return None

    total_shift_records = {}
    for entry in data:
        total_shift_records.setdefault(entry.shift, 0)
        total_shift_records[entry.shift] += 1

    labels = [_(d) for d in list(total_shift_records)]
    chart = {
        "data": {"labels": labels, "datasets": [{"name": _("Shift"), "values": list(total_shift_records.values())}]},
        "type": "percentage",
    }
    return chart

def get_attendance_with_checkins(filters):
    attendance = frappe.qb.DocType("Attendance")
    checkin = frappe.qb.DocType("Employee Checkin").as_("checkin1")  # alias here
    shift_type = frappe.qb.DocType("Shift Type")

    query = (
        get_base_attendance_query(filters)
        .inner_join(checkin)
        .on(checkin.attendance == attendance.name)
        .select(
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
    )

    # filters
    if getattr(filters, "late_entry", False) and not filters.consider_grace_period:
        query = query.where(attendance.in_time > checkin.shift_start)
    if getattr(filters, "early_exit", False) and not filters.consider_grace_period:
        query = query.where(attendance.out_time < checkin.shift_end)

    return query.run(as_dict=True)


def get_base_attendance_query(filters):
    attendance = frappe.qb.DocType("Attendance")
    checkin = frappe.qb.DocType("Employee Checkin").as_("checkin_base")  # alias
    shift_type = frappe.qb.DocType("Shift Type")

    query = (
        frappe.qb.from_(attendance)
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

    for field in filters:
        if field == "from_date":
            query = query.where(attendance.attendance_date >= filters.from_date)
        elif field == "to_date":
            query = query.where(attendance.attendance_date <= filters.to_date)
        elif field in ["consider_grace_period", "include_attendance_without_checkins"]:
            continue
        else:
            query = query.where(attendance[field] == filters[field])

    # query = query.where(Criterion.all(build_qb_match_conditions("Attendance")))
	
    return query

def get_attendance_without_checkins(filters):
    attendance = frappe.qb.DocType("Attendance")
    checkin = frappe.qb.DocType("Employee Checkin")

    query = (
        get_base_attendance_query(filters)
        .left_join(checkin)
        .on(checkin.attendance == attendance.name)
        .where(checkin.attendance.isnull())
    )
    return query.run(as_dict=True)


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

    if not start or not end:
        return start, end

    # convert datetime → time
    if hasattr(start, "time"):
        start = start.time()

    if hasattr(end, "time"):
        end = end.time()

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


