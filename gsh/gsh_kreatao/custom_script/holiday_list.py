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
