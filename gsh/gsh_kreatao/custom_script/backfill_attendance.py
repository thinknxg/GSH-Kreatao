import frappe
from frappe.utils import getdate, today
from datetime import timedelta

def backfill():
    shift_types = ["Weekly Off", "Public Holiday", "NIGHT OFF"]

    shift_assignments = frappe.get_all(
        "Shift Assignment",
        filters={"shift_type": ["in", shift_types], "docstatus": 1},
        fields=["employee", "shift_type", "start_date", "end_date"]
    )

    created = 0
    skipped = 0

    for assignment in shift_assignments:
        start = getdate(assignment.start_date)
        end = getdate(assignment.end_date or today())
        if end > getdate(today()):
            end = getdate(today())

        current = start
        while current <= end:
            exists = frappe.db.exists("Attendance", {
                "employee": assignment.employee,
                "attendance_date": current,
                "docstatus": ["!=", 2]
            })
            if not exists:
                try:
                    att = frappe.get_doc({
                        "doctype": "Attendance",
                        "employee": assignment.employee,
                        "attendance_date": current,
                        "status": "Absent",
                        "shift": assignment.shift_type
                    })
                    att.insert(ignore_permissions=True)
                    att.submit()
                    created += 1
                    frappe.db.commit()
                except Exception as e:
                    frappe.log_error(f"Backfill failed for {assignment.employee} on {current}: {str(e)}", "Backfill Attendance")
            else:
                skipped += 1
            current += timedelta(days=1)

    print(f"Done. Created: {created}, Skipped (already exists): {skipped}")


def check():
    result = frappe.db.sql("""
        SELECT status, shift, COUNT(*) as count 
        FROM `tabAttendance` 
        WHERE shift IN ('Weekly Off', 'NIGHT OFF', 'Public Holiday') 
        AND docstatus != 2 
        GROUP BY status, shift
    """, as_dict=True)
    for row in result:
        print(f"Status: {row.status} | Shift: {row.shift} | Count: {row.count}")


def check_all():
    result = frappe.db.sql("""
        SELECT status, COUNT(*) as count 
        FROM `tabAttendance` 
        WHERE docstatus != 2 
        GROUP BY status
    """, as_dict=True)
    for row in result:
        print(f"Status: {row.status} | Count: {row.count}")


def fix_status():
    wrong_records = frappe.db.sql("""
        SELECT name, employee, attendance_date, shift
        FROM `tabAttendance`
        WHERE shift IN ('Weekly Off', 'NIGHT OFF', 'Public Holiday')
        AND status != 'Absent'
        AND docstatus = 1
    """, as_dict=True)

    fixed = 0
    failed = 0

    for row in wrong_records:
        try:
            att = frappe.get_doc("Attendance", row.name)
            att.cancel()
            frappe.db.commit()

            new_att = frappe.get_doc({
                "doctype": "Attendance",
                "employee": row.employee,
                "attendance_date": row.attendance_date,
                "status": "Absent",
                "shift": row.shift
            })
            new_att.insert(ignore_permissions=True)
            new_att.submit()
            frappe.db.commit()
            fixed += 1
        except Exception as e:
            frappe.log_error(f"Fix failed for {row.name}: {str(e)}", "Fix Attendance Status")
            failed += 1

    print(f"Done. Fixed: {fixed}, Failed: {failed}")

def debug_link():
    # Check attendance for EMP29 on 2026-05-07
    rows = frappe.db.sql("""
        SELECT name, docstatus, status, shift 
        FROM `tabAttendance` 
        WHERE employee='EMP29' AND attendance_date='2026-05-07'
    """, as_dict=True)
    for r in rows:
        print(f"Attendance: {r.name} | docstatus: {r.docstatus} | status: {r.status} | shift: {r.shift}")

    # Check where Frappe finds the link
    links = frappe.db.sql("""
        SELECT name, link_doctype, link_name 
        FROM `tabDynamic Link` 
        WHERE link_doctype='Shift Assignment' AND link_name='HR-SHA-26-05-00006'
    """, as_dict=True)
    for r in links:
        print(f"Dynamic Link: {r.name} | {r.link_doctype} | {r.link_name}")
