import frappe

def update_other_holiday_lists(doc, method):
    # Only run if the list is "Public Holiday"
    if doc.name != "Public Holiday":
        return

    # Get all holiday lists except "Public Holiday"
    other_holiday_lists = frappe.get_all("Holiday List", filters={"name": ["!=", "Public Holiday"]})

    # Loop through each holiday in this list
    for holiday in doc.holidays:
        for hl in other_holiday_lists:
            # Check if this holiday date exists in the other list
            exists = frappe.db.exists("Holiday", {
                "parent": hl.name,
                "holiday_date": holiday.holiday_date
            })

            if not exists:
                # Append holiday to the other list
                target_list = frappe.get_doc("Holiday List", hl.name)
                target_list.append("holidays", {
                    "holiday_date": holiday.holiday_date,
                    "description": "Public Holiday"
                })
                target_list.save(ignore_permissions=True)


WO_NO_DESCRIPTIONS = ["Weekly Off", "NIGHT OFF", "On Call Shift", "On Call Day", "On Call Night"]

def cancel_shift_assignments_for_removed_wo_no(doc, method):
    """When WO/NO entries are removed from a holiday list, cancel the linked shift assignments."""
    old_doc = doc.get_doc_before_save()
    if not old_doc:
        return

    old_dates = {
        (h.holiday_date, h.description): h
        for h in old_doc.holidays
        if h.description in WO_NO_DESCRIPTIONS
    }
    new_dates = {
        (h.holiday_date, h.description): h
        for h in doc.holidays
        if h.description in WO_NO_DESCRIPTIONS
    }

    removed = set(old_dates.keys()) - set(new_dates.keys())
    if not removed:
        return

    # Find which employee owns this holiday list
    employees = frappe.get_all("Employee", filters={"holiday_list": doc.name}, pluck="name")

    for employee in employees:
        for (holiday_date, shift_type) in removed:
            # Find submitted shift assignment covering this date
            assignments = frappe.get_all("Shift Assignment", filters={
                "employee": employee,
                "shift_type": shift_type,
                "start_date": ["<=", holiday_date],
                "docstatus": 1,
            }, or_filters=[
                {"end_date": [">=", holiday_date]},
                {"end_date": ["is", "not set"]},
            ], pluck="name")

            for assignment in assignments:
                try:
                    sa_doc = frappe.get_doc("Shift Assignment", assignment)
                    sa_doc.flags.ignore_links = True
                    sa_doc.cancel()
                    frappe.db.commit()
                    frappe.msgprint(f"Auto-cancelled Shift Assignment {assignment} for {employee} on {holiday_date}", alert=True)
                except Exception as e:
                    frappe.log_error(str(e), "Auto Cancel Shift Assignment")
