import json
import frappe
from frappe.utils import getdate, add_days

OFF_SHIFT_TYPES = ["Weekly Off", "Night Off"]

def execute(filters=None):
    filters = filters or {}
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))
    department = filters.get("department")

    columns = [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 150},
        {"label": "Total Unmarked Days", "fieldname": "total_unmarked", "fieldtype": "HTML", "width": 160},
        {"label": "unmarked_dates_json", "fieldname": "unmarked_dates_json", "fieldtype": "Data", "width": 0, "hidden": 1},
    ]

    emp_filters = {"status": "Active"}
    if department:
        emp_filters["department"] = department

    employees = frappe.get_all(
        "Employee",
        filters=emp_filters,
        fields=["name", "employee_name", "department", "date_of_joining", "relieving_date", "holiday_list"]
    )
    employee_ids = [e.name for e in employees]

    marked_by_date = {}
    d = from_date
    while d <= to_date:
        marked_by_date[d] = set(frappe.get_all("Attendance", filters={"attendance_date": d}, pluck="employee"))
        d = add_days(d, 1)

    # WO/NO from Shift Assignment
    shift_assignments = frappe.get_all(
        "Shift Assignment",
        filters={
            "employee": ["in", employee_ids],
            "shift_type": ["in", OFF_SHIFT_TYPES],
            "docstatus": 1,
            "start_date": ["<=", to_date],
        },
        fields=["employee", "shift_type", "start_date", "end_date"]
    )

    off_dates_by_employee = {}
    for sa in shift_assignments:
        start = sa.start_date
        end = sa.end_date or sa.start_date
        if end < from_date:
            continue
        d2 = max(start, from_date)
        end_clamped = min(end, to_date)
        emp_off = off_dates_by_employee.setdefault(sa.employee, set())
        while d2 <= end_clamped:
            emp_off.add(d2)
            d2 = add_days(d2, 1)

    # Holiday List dates per distinct holiday list used by these employees
    holiday_lists = list({e.holiday_list for e in employees if e.holiday_list})
    holidays_by_list = {}
    if holiday_lists:
        all_holidays = frappe.get_all(
            "Holiday",
            filters={
                "parent": ["in", holiday_lists],
                "holiday_date": ["between", [from_date, to_date]],
            },
            fields=["parent", "holiday_date"]
        )
        for h in all_holidays:
            holidays_by_list.setdefault(h.parent, set()).add(h.holiday_date)

    data = []
    for emp in employees:
        emp_off_dates = off_dates_by_employee.get(emp.name, set())
        emp_holiday_dates = holidays_by_list.get(emp.holiday_list, set()) if emp.holiday_list else set()

        unmarked_iso = []
        d = from_date
        while d <= to_date:
            if emp.date_of_joining and d < emp.date_of_joining:
                d = add_days(d, 1)
                continue
            if emp.relieving_date and d > emp.relieving_date:
                d = add_days(d, 1)
                continue
            if d in emp_off_dates or d in emp_holiday_dates:
                d = add_days(d, 1)
                continue
            if emp.name not in marked_by_date[d]:
                unmarked_iso.append(str(d))
            d = add_days(d, 1)

        if unmarked_iso:
            count = len(unmarked_iso)
            total_html = (
                f"<a href='#' class='unmarked-count-link' "
                f"data-employee='{emp.name}' "
                f"data-employee-name='{frappe.utils.escape_html(emp.employee_name)}' "
                f"style='font-weight:600; color:#2490ef; text-decoration:underline; cursor:pointer;'>"
                f"{count}</a>"
            )
            data.append({
                "employee": emp.name,
                "employee_name": emp.employee_name,
                "department": emp.department,
                "total_unmarked": total_html,
                "unmarked_dates_json": json.dumps(unmarked_iso),
            })

    data.sort(key=lambda x: len(json.loads(x["unmarked_dates_json"])), reverse=True)

    return columns, data
