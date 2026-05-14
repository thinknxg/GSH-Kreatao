# GSH Override for Shift Attendance Report
# Only overrides get_data to add WO/NO status for Weekly Off and Night Off shifts
# Original: hrms/hr/report/shift_attendance/shift_attendance.py

from hrms.hr.report.shift_attendance.shift_attendance import (
    get_columns,
    get_attendance_with_checkins,
    get_attendance_without_checkins,
    update_data,
    get_chart_data,
    get_report_summary,
)


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    report_summary = get_report_summary(data)
    return columns, data, None, chart, report_summary


def get_data(filters):
    data = get_attendance_with_checkins(filters)
    data = update_data(data, filters)

    if filters.include_attendance_without_checkins:
        without_checkins = get_attendance_without_checkins(filters)
        for d in without_checkins:
            if d.status == "Present" and d.shift == "Weekly Off":
                d.status = "WO"
            elif d.status == "Present" and d.shift == "NIGHT OFF":
                d.status = "NO"
        data.extend(without_checkins)

    return data
