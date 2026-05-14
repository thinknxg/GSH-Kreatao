# GSH Override for Monthly Attendance Sheet
# Patches HRMS module before execute is called

import frappe
from frappe.utils import getdate
from datetime import date

# Change 1: status_map with Night Off added
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


# Change 2: colors with Night Off color
def get_message() -> str:
    message = ""
    colors = [
        "green", "red", "orange", "#914EE3", "green",
        "#3187D8", "#878787", "#878787", "#1a1a6e",
    ]
    count = 0
    for status, abbr in status_map.items():
        message += f"""
            <span style='border-left: 2px solid {colors[count]}; padding-right: 12px; padding-left: 5px; margin-right: 3px;'>
                {frappe._(status)} - {abbr}
            </span>
        """
        count += 1
    return message


# Change 3: get_holiday_status with Night Off check
def get_holiday_status(holiday_date: date, holidays: list) -> str:
    status = None
    if holidays:
        for holiday in holidays:
            if holiday_date == holiday.get("holiday_date"):
                if holiday.get("weekly_off"):
                    if holiday.get("description") == "NIGHT OFF":
                        status = "Night Off"
                    else:
                        status = "Weekly Off"
                else:
                    status = "Holiday"
                break
    return status


def _patch_mas_module():
    import hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet as mas

    # Patch status_map and functions
    mas.status_map = status_map
    mas.get_message = get_message
    mas.get_holiday_status = get_holiday_status

    # Change 4: patch get_attendance_status_for_detailed_view
    from hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet import get_dates_in_period

    def get_attendance_status_for_detailed_view(employee, filters, employee_attendance, holidays):
        total_days = get_dates_in_period(filters)
        attendance_values = []
        for shift, status_dict in employee_attendance.items():
            row = {"shift": shift}
            for d in total_days:
                d = getdate(d)
                status = status_dict.get(d)
                if shift == "NIGHT OFF" and status == "Present":
                    status = "Night Off"
                if status is None and holidays:
                    status = get_holiday_status(d, holidays)
                abbr = status_map.get(status, "")
                row[d.strftime("%d-%m-%Y")] = abbr
            attendance_values.append(row)
        return attendance_values

    mas.get_attendance_status_for_detailed_view = get_attendance_status_for_detailed_view

    # Change 5: patch get_attendance_status_for_summarized_view
    from hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet import get_attendance_summary_and_days

    def get_attendance_status_for_summarized_view(employee, filters, holidays, joined_in_current_period, joined_date):
        summary, attendance_days = get_attendance_summary_and_days(employee, filters)
        if not any(summary.values()):
            return {}
        total_days = get_dates_in_period(filters)
        total_holidays = total_unmarked_days = 0
        for d in total_days:
            d = getdate(d)
            if d.day in attendance_days or (joined_in_current_period and d < joined_date):
                continue
            status = get_holiday_status(d, holidays)
            if status in ["Weekly Off", "Night Off", "Holiday"]:
                total_holidays += 1
            elif not status:
                total_unmarked_days += 1
        return {
            "total_present": summary.total_present + summary.total_half_days,
            "total_leaves": summary.total_leaves + summary.total_half_days,
            "total_absent": summary.total_absent,
            "total_holidays": total_holidays,
            "unmarked_days": total_unmarked_days,
        }

    mas.get_attendance_status_for_summarized_view = get_attendance_status_for_summarized_view


def execute(filters=None):
    _patch_mas_module()
    from hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet import execute as original_execute
    return original_execute(filters)
