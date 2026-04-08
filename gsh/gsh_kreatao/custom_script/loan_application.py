from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate

def update_custom_approval_fields(doc, method):
    from frappe.utils import now_datetime

    def get_full_name(user):
        return frappe.db.get_value("User", user, "full_name")

    if doc.loan == "Approved By Accounts Manager":
        doc.custom_approved_by_accounts_manager = frappe.session.user
        doc.custom_accounts_manager_date = now_datetime()
        doc.custom_accounts_manager_name = get_full_name(frappe.session.user)
    


def update_custom_approval_approved(doc, method):
    from frappe.utils import now_datetime

    def get_full_name_approved(user):
        return frappe.db.get_value("User", user, "full_name")
   
    if doc.loan == "Approved":
        doc.custom_approved = frappe.session.user
        doc.custom_approved_date = now_datetime()
        doc.custom_approved_name = get_full_name_approved(frappe.session.user)


