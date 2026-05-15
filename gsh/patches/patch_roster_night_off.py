"""
Patch: Show NO instead of WO for NIGHT OFF in Roster MonthViewTable.vue
Runs automatically on bench migrate via patches.txt
"""
import os

def execute():
    import frappe
    # get_app_path returns apps/hrms/hrms — we need apps/hrms
    hrms_app_path = os.path.join(frappe.get_app_path("hrms"), "..")
    vue_path = os.path.abspath(os.path.join(hrms_app_path, "roster", "src", "components", "MonthViewTable.vue"))

    if not os.path.exists(vue_path):
        print(f"Skipping: {vue_path} not found")
        return

    content = open(vue_path).read()

    old = "? '<strong>WO</strong>'"
    new = "? (events.data[employee.name][day.date].description === 'NIGHT OFF' ? '<strong>NO</strong>' : '<strong>WO</strong>')"

    if new in content:
        print("MonthViewTable.vue already patched, skipping.")
        return

    if old not in content:
        print("Pattern not found in MonthViewTable.vue — may have changed upstream.")
        return

    content = content.replace(old, new)
    open(vue_path, "w").write(content)
    print("MonthViewTable.vue patched — NIGHT OFF shows as NO in Roster.")
