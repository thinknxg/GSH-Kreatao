import frappe


def execute(filters=None):
    filters = frappe._dict(filters or {})
    if not filters.get("status"):
        filters["status"] = "Approved"

    conditions = get_conditions(filters)
    attendance_conditions = get_attendance_conditions(filters)

    raw_data = frappe.db.sql("""
        select
            la.employee as employee,
            la.employee_name as employee_name,
            la.department as department,
            la.leave_type as leave_type,
            sum(la.total_leave_days) as total_days
        from `tabLeave Application` la
        where la.docstatus = 1 {conditions}
        group by la.employee, la.leave_type
        order by la.employee_name
    """.format(conditions=conditions), filters, as_dict=1)

    absent_data = frappe.db.sql("""
        select
            att.employee as employee,
            count(*) as absent_days
        from `tabAttendance` att
        where att.docstatus = 1
        and att.status = 'Absent'
        {attendance_conditions}
        group by att.employee
    """.format(attendance_conditions=attendance_conditions), filters, as_dict=1)

    absent_map = {row.employee: row.absent_days for row in absent_data}

    all_emp_ids = list(absent_map.keys())
    emp_details = {}
    if all_emp_ids:
        emp_records = frappe.db.sql("""
            select name, employee_name, department
            from `tabEmployee`
            where name in ({})
        """.format(", ".join(["%s"] * len(all_emp_ids))), all_emp_ids, as_dict=1)
        emp_details = {e.name: e for e in emp_records}

    leave_types = sorted(set(row.leave_type for row in raw_data if row.leave_type))

    columns = get_columns(leave_types)
    data = get_pivoted_data(raw_data, leave_types, absent_map, emp_details)

    return columns, data


def get_columns(leave_types):
    columns = [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 160},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 150},
    ]
    for lt in leave_types:
        columns.append({
            "label": lt,
            "fieldname": frappe.scrub(lt),
            "fieldtype": "Float",
            "width": 120
        })
    columns.append({"label": "Absent Days", "fieldname": "absent_days", "fieldtype": "Float", "width": 120})
    columns.append({"label": "Total Leave Days", "fieldname": "total_leave_days", "fieldtype": "Float", "width": 130})
    return columns


def get_pivoted_data(raw_data, leave_types, absent_map, emp_details):
    employee_map = {}

    for row in raw_data:
        emp = row.employee
        if emp not in employee_map:
            employee_map[emp] = {
                "employee": emp,
                "employee_name": row.employee_name,
                "department": row.department,
                "absent_days": absent_map.get(emp, 0),
                "total_leave_days": 0
            }
            for lt in leave_types:
                employee_map[emp][frappe.scrub(lt)] = 0

        if row.leave_type:
            fieldname = frappe.scrub(row.leave_type)
            employee_map[emp][fieldname] = row.total_days
            employee_map[emp]["total_leave_days"] += row.total_days

    for emp, days in absent_map.items():
        if emp not in employee_map:
            details = emp_details.get(emp, {})
            employee_map[emp] = {
                "employee": emp,
                "employee_name": details.get("employee_name", ""),
                "department": details.get("department", ""),
                "absent_days": days,
                "total_leave_days": 0
            }
            for lt in leave_types:
                employee_map[emp][frappe.scrub(lt)] = 0

    for emp in employee_map:
        employee_map[emp]["total_leave_days"] += absent_map.get(emp, 0)

    return sorted(employee_map.values(), key=lambda x: x.get("employee_name") or "")


def get_conditions(filters):
    conditions = ""
    if filters.get("status"):
        conditions += " and la.status = %(status)s"
    if filters.get("from_date"):
        conditions += " and la.from_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " and la.to_date <= %(to_date)s"
    if filters.get("company"):
        conditions += " and la.company = %(company)s"
    if filters.get("department"):
        conditions += " and la.department = %(department)s"
    if filters.get("employee"):
        conditions += " and la.employee = %(employee)s"
    if filters.get("leave_type"):
        conditions += " and la.leave_type = %(leave_type)s"
    return conditions


def get_attendance_conditions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += " and att.attendance_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " and att.attendance_date <= %(to_date)s"
    if filters.get("company"):
        conditions += " and att.company = %(company)s"
    if filters.get("department"):
        conditions += " and att.department = %(department)s"
    if filters.get("employee"):
        conditions += " and att.employee = %(employee)s"
    return conditions
