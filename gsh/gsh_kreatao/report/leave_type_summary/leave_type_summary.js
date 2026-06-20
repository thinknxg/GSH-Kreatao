frappe.query_reports["Leave Type Summary"] = {
"filters": [
{
"fieldname": "from_date",
"label": "From Date",
"fieldtype": "Date",
"default": frappe.datetime.year_start()
},
{
"fieldname": "to_date",
"label": "To Date",
"fieldtype": "Date",
"default": frappe.datetime.get_today()
},
{
"fieldname": "company",
"label": "Company",
"fieldtype": "Link",
"options": "Company",
"default": frappe.defaults.get_user_default("Company")
},
{
"fieldname": "department",
"label": "Department",
"fieldtype": "Link",
"options": "Department"
},
{
"fieldname": "employee",
"label": "Employee",
"fieldtype": "Link",
"options": "Employee"
},
{
"fieldname": "leave_type",
"label": "Leave Type",
"fieldtype": "Link",
"options": "Leave Type"
},
{
"fieldname": "include_absent",
"label": "Include Absent Days",
"fieldtype": "Check",
"default": 1
},
{
"fieldname": "status",
"label": "Status",
"fieldtype": "Select",
"options": "\nApproved\nRejected\nOpen\nCancelled",
"default": "Approved"
}
]
};
