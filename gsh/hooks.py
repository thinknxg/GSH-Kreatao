app_name = "gsh"
app_title = "GSH Kreatao"
app_publisher = "Rawas"
app_description = "GSH"
app_email = "rawasrazak3@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/gsh/css/gsh.css"
# app_include_js = "/assets/gsh/js/gsh.js"

# include js, css files in header of web template
# web_include_css = "/assets/gsh/css/gsh.css"
# web_include_js = "/assets/gsh/js/gsh.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "gsh/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
doctype_js = {
    "Salary Slip": "public/js/salary_slip.js",
    "Payroll Entry": "public/js/payroll_entry.js",
    "Shift Assignment": "public/js/shift_assignment.js",
    "Attendance Request": "public/js/attendance_request.js",
    # "Compensatory Off": "public/js/co_l.js"
}
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "gsh/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "gsh.utils.jinja_methods",
# 	"filters": "gsh.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "gsh.install.before_install"
# after_install = "gsh.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "gsh.uninstall.before_uninstall"
# after_uninstall = "gsh.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "gsh.utils.before_app_install"
# after_app_install = "gsh.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "gsh.utils.before_app_uninstall"
# after_app_uninstall = "gsh.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "gsh.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events


doc_events = {
    "Attendance": {
        "on_submit": "gsh.gsh_kreatao.custom_script.attendance.calculate_hours",
        "on_update_after_submit": "gsh.gsh_kreatao.custom_script.attendance.create_compensatory_leave"
    },
    "Employee Checkin": {
        "before_save": "gsh.gsh_kreatao.custom_script.employee_checkin.fetch_shift_assignment"
    },
    "Leave Application": {
        "before_save": "gsh.gsh_kreatao.custom_script.leave_application.update_custom_approval_fields",
        "before_submit": "gsh.gsh_kreatao.custom_script.leave_application.update_custom_approval_approved"
    },
    "Loan Application": {
        "before_save": "gsh.gsh_kreatao.custom_script.loan_application.update_custom_approval_fields",
        "before_submit": "gsh.gsh_kreatao.custom_script.loan_application.update_custom_approval_approved"
    },
    "Shift Assignment": {
        "after_insert": "gsh.gsh_kreatao.custom_script.shift_assignment.add_shift_assignment_date_to_holiday_list",
        "on_cancel": "gsh.gsh_kreatao.custom_script.shift_assignment.remove_shift_assignment_dates_from_holiday_list",
        "on_update_after_submit": "gsh.gsh_kreatao.custom_script.shift_assignment.update_shift_assignment_dates_in_holiday_list"
    },
    "Holiday List": {
        "validate": "gsh.gsh_kreatao.custom_script.holiday_list.update_other_holiday_lists"
    }
}

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#     "cron": {
#         "59 23 * * *": [
#             "gsh.gsh_kreatao.custom_script.mark_attendance.schedule_mark_attendance"
#         ]
#     }
# }

# scheduler_events = {
# 	"all": [
# 		"gsh.tasks.all"
# 	],
# 	"daily": [
# 		"gsh.tasks.daily"
# 	],
# 	"hourly": [
# 		"gsh.tasks.hourly"
# 	],
# 	"weekly": [
# 		"gsh.tasks.weekly"
# 	],
# 	"monthly": [
# 		"gsh.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "gsh.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "gsh.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "gsh.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["gsh.utils.before_request"]
# after_request = ["gsh.utils.after_request"]

# Job Events
# ----------
# before_job = ["gsh.utils.before_job"]
# after_job = ["gsh.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"gsh.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

fixtures=[
    {
    	"doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [ 
                    "Employee Checkin-custom_shift_assignment",
                    "Attendance-custom_over_time_hours",
                    "Attendance-custom_late_entry_hours",
                    "Shift Assignment-custom_holiday",
                    "Attendance-custom_total_hours",
                    "Attendance-custom_approved",
                    "Attendance-custom_is_paid",
                    "Attendance-custom_is_compensatory_leave",
                    "Employee-custom_over_time_rate",
                    "Employee-custom_late_entry_rate",
                    "Attendance Request-custom_overtime_hours",
                    "Shift Type-custom_split_shift",
                    "Shift Type-custom_break_start_time",
                    "Shift Type-custom_break_end_time"
                    
                 ]
            ]
        ]
    }
]
