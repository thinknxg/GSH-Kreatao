from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate

def update_custom_approval_fields(doc, method):
    from frappe.utils import now_datetime

    def get_full_name(user):
        return frappe.db.get_value("User", user, "full_name")

    if doc.leave_application == "Approved by Incharge":
        doc.custom_approved_by_incharge = frappe.session.user
        doc.custom_incharge_date = now_datetime()
        doc.custom_incharge_name = get_full_name(frappe.session.user)
    
    elif doc.leave_application == "Approved by HOD":
        doc.custom_approved_by_hod = frappe.session.user
        doc.custom_hod_date = now_datetime()
        doc.custom_hod_name = get_full_name(frappe.session.user)
    
    elif doc.leave_application == "Approved by Operation Manager":
        doc.custom_approved_by_operation_manager = frappe.session.user
        doc.custom_operation_manager_date = now_datetime()
        doc.custom_operation_manager_name = get_full_name(frappe.session.user)


def update_custom_approval_approved(doc, method):
    from frappe.utils import now_datetime

    def get_full_name_approved(user):
        return frappe.db.get_value("User", user, "full_name")
   
    if doc.leave_application == "Approved":
        doc.custom_approved = frappe.session.user
        doc.custom_approved_date = now_datetime()
        doc.custom_approved_name = get_full_name_approved(frappe.session.user)
