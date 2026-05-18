
import frappe
from datetime import datetime, timedelta
import calendar

def execute(filters=None):
    if not filters:
        filters = {}

    # Determine date range based on from_date/to_date or month/year
    if filters.get("from_date") and filters.get("to_date"):
        first_day = datetime.strptime(filters["from_date"], "%Y-%m-%d").date()
        last_day = datetime.strptime(filters["to_date"], "%Y-%m-%d").date()
    else:
        year = int(filters.get("year"))
        month_name = filters.get("month")
        month = get_month_number(month_name)
        first_day = datetime(year, month, 1).date()
        last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()

    columns = get_columns(first_day, last_day)
    data = get_data(filters, first_day, last_day)

    return columns, data

def get_month_number(month_name):
    """Convert month name to month number"""
    return list(calendar.month_name).index(month_name)

def get_columns(first_day, last_day):
    """Generate dynamic columns for the roster based on date range"""
    columns = [{
        "label": "Employee",
        "fieldname": "employee",
        "fieldtype": "Data",
        "width": 180
    }]

    total_days = (last_day - first_day).days + 1
    for i in range(total_days):
        date_obj = first_day + timedelta(days=i)
        day_name = date_obj.strftime("%a")
        label = f"{day_name} {date_obj.day:02d}"
        columns.append({
            "label": label,
            "fieldname": f"day_{i+1}",
            "fieldtype": "HTML",
            "width": 160
        })

    return columns

def get_data(filters, first_day, last_day):
    """Fetch roster data including shifts, leaves, and holidays"""
    company = filters.get("company")
    department = filters.get("department")

    # Employee filters
    employee_conditions = {}
    if department:
        employee_conditions["department"] = department
    if company:
        employee_conditions["company"] = company

    employee_list = frappe.get_all(
        "Employee",
        filters=employee_conditions,
        fields=["name", "employee_name"]
    )

    if not employee_list:
        return []

    employee_ids = [e.name for e in employee_list]

    # Fetch Shift Assignments
    assignments = frappe.db.sql("""
        SELECT
            sa.employee,
            e.employee_name,
            sa.shift_type,
            sa.start_date,
            sa.end_date,
            st.custom_break_start_time,
            st.custom_break_end_time
        FROM `tabShift Assignment` sa
        JOIN `tabEmployee` e ON sa.employee = e.name
        LEFT JOIN `tabShift Type` st ON sa.shift_type = st.name
        WHERE sa.docstatus = 1
        AND sa.employee IN %(employee_ids)s
        AND sa.start_date <= %(last_day)s
        AND (sa.end_date IS NULL OR sa.end_date >= %(first_day)s)
    """, {
        "employee_ids": tuple(employee_ids),
        "first_day": first_day,
        "last_day": last_day
    }, as_dict=1)

    # Fetch Approved Leave
    leaves = frappe.db.sql("""
        SELECT employee, from_date, to_date
        FROM `tabLeave Application`
        WHERE docstatus = 1
        AND status = 'Approved'
        AND employee IN %(employee_ids)s
        AND from_date <= %(last_day)s
        AND to_date >= %(first_day)s
    """, {
        "employee_ids": tuple(employee_ids),
        "first_day": first_day,
        "last_day": last_day
    }, as_dict=1)

    # Fetch Holidays — per employee holiday list
    default_holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")
    emp_holiday_lists = {
        e.name: frappe.db.get_value("Employee", e.name, "holiday_list") or default_holiday_list
        for e in employee_list
    }
    all_holiday_lists = list(set(emp_holiday_lists.values()))
    holiday_map_by_list = {}
    for hl in all_holiday_lists:
        if not hl:
            continue
        rows = frappe.db.sql("""
            SELECT holiday_date, description, weekly_off, custom_night_off
            FROM `tabHoliday`
            WHERE parent = %s
            AND holiday_date BETWEEN %s AND %s
        """, (hl, first_day, last_day), as_dict=1)
        holiday_map_by_list[hl] = {r.holiday_date: r for r in rows}

    total_days = (last_day - first_day).days + 1
    employee_map = {}

    # Create Leave Map (Optimized)
    leave_map = {}
    for leave in leaves:
        leave_map.setdefault(leave.employee, []).append(leave)

    # Initialize all employees
    for emp in employee_list:
        emp_display = f"{emp.employee_name} ({emp.name})"
        employee_map[emp_display] = {"employee": emp_display}

        emp_hl = emp_holiday_lists.get(emp.name, default_holiday_list)
        holiday_map = holiday_map_by_list.get(emp_hl, {})

        for i in range(total_days):
            date_obj = first_day + timedelta(days=i)
            fieldname = f"day_{i+1}"

            # Holiday / Weekly Off / Night Off
            if date_obj in holiday_map:
                h = holiday_map[date_obj]
                if h.get("custom_night_off"):
                    employee_map[emp_display][fieldname] = "<span style='color:#8B008B; font-weight:bold;'>NO</span>"
                elif h.get("weekly_off"):
                    employee_map[emp_display][fieldname] = "<span style='color:blue; font-weight:bold;'>WO</span>"
                else:
                    employee_map[emp_display][fieldname] = f"<span style='color:purple;'>{h.description}</span>"

            # Leave
            elif any(
                    leave.from_date <= date_obj <= leave.to_date
                    for leave in leave_map.get(emp.name, [])
                ):
                
                employee_map[emp_display][fieldname] = "<span style='color:green; font-weight:bold;'>L</span>"

            # Default NA
            else:
                employee_map[emp_display][fieldname] = "<span style='color:red; font-weight:bold;'>NA</span>"

    # Apply Shift Assignments (override only NA)
    for row in assignments:
        emp_display = f"{row.employee_name} ({row.employee})"
        current_date = max(row.start_date, first_day)
        end_date = row.end_date if row.end_date else last_day

        while current_date <= min(end_date, last_day):
            day_index = (current_date - first_day).days + 1
            fieldname = f"day_{day_index}"

            if "NA" in employee_map[emp_display][fieldname]:
                employee_map[emp_display][fieldname] = row.shift_type

            current_date += timedelta(days=1)

    return list(employee_map.values())