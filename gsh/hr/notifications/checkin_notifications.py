import frappe
from frappe.utils import get_url_to_form, formatdate, get_datetime


def on_checkin_update(doc, method):
    """
    Fires on every Employee Checkin save.
    Sends Off-Shift alert only when offshift == 1.
    """
    if not doc.offshift:
        return

    recipients = _get_recipients(doc)
    if not recipients:
        frappe.log_error(
            f"Off-Shift notification: No recipients found for {doc.name}",
            "Off-Shift Alert"
        )
        return

    subject, message = _build_email(doc)

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message,
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        now=False
    )


# ── Recipients ────────────────────────────────────────────────────────────────

def _get_recipients(doc):
    recipients = []

    # Employee's own user email
    employee_email = frappe.db.get_value("Employee", doc.employee, "user_id")
    if employee_email:
        recipients.append(employee_email)

    # Leave Approver
    leave_approver = frappe.db.get_value("Employee", doc.employee, "leave_approver")
    if leave_approver:
        recipients.append(leave_approver)

    return list(set(recipients))


# ── Email Content ─────────────────────────────────────────────────────────────

def _build_email(doc):
    checkin_time = get_datetime(doc.time)
    formatted_date = formatdate(checkin_time, "dd-MMM-yyyy")
    formatted_time = checkin_time.strftime("%H:%M")
    doc_link = get_url_to_form("Employee Checkin", doc.name)

    subject = f"Off-Shift Alert: {doc.employee_name} on {formatted_date}"

    message = f"""
    <p>Dear {doc.employee_name},</p>

    <p>An <strong>Off-Shift</strong> check-in has been recorded. Please review the details below.</p>

    <table border="1" cellpadding="8" cellspacing="0"
           style="border-collapse:collapse; font-family:Arial, sans-serif; font-size:14px; min-width:400px;">
        <tr style="background:#f5f5f5;">
            <td><strong>Employee</strong></td>
            <td>{doc.employee_name} ({doc.employee})</td>
        </tr>
        <tr>
            <td><strong>Date</strong></td>
            <td>{formatted_date}</td>
        </tr>
        <tr style="background:#f5f5f5;">
            <td><strong>Time</strong></td>
            <td>{formatted_time}</td>
        </tr>
        <tr>
            <td><strong>Shift</strong></td>
            <td>{doc.shift or "N/A"}</td>
        </tr>
        <tr style="background:#f5f5f5;">
            <td><strong>Log Type</strong></td>
            <td>{doc.log_type or "N/A"}</td>
        </tr>
    </table>

    <br>
    <a href="{doc_link}"
       style="background:#4263EB; color:white; padding:10px 20px;
              text-decoration:none; border-radius:4px; font-family:Arial; font-size:14px;">
        View Check-in Record
    </a>

    <p style="color:#aaa; font-size:12px; margin-top:24px;">
        This is an automated notification from the HR system.
    </p>
    """

    return subject, message
