
frappe.query_reports["Shift Attendance Detail"] = {

	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.month_start(),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.month_end(),
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
		},
		{
			fieldname: "shift",
			label: __("Shift Type"),
			fieldtype: "Link",
			options: "Shift Type",
		},
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department",
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "late_entry",
			label: __("Late Entry"),
			fieldtype: "Check",
		},
		{
			fieldname: "early_exit",
			label: __("Early Exit"),
			fieldtype: "Check",
		},
		{
			fieldname: "consider_grace_period",
			label: __("Consider Grace Period"),
			fieldtype: "Check",
			default: 1,
		},
	],
	formatter: (value, row, column, data, default_formatter) => {
		value = default_formatter(value, row, column, data);
		if (
			(column.fieldname === "in_time" && data.late_entry) ||
			(column.fieldname === "out_time" && data.early_exit) ||
			(column.fieldname === "first_shift_end" && data.first_shift_early_exit) ||
			(column.fieldname === "second_shift_start" && data.second_shift_late_entry)
		) {
			value = `<span style='color:red!important'>${value}</span>`;
		}

		if (column.fieldname === "status" && data && data.status) {
			const status_colors = {
				"P": "#2ecc71",   // Green
				"A": "#e74c3c",   // Red
				"HD/A": "#d35400",// Dark Orange
				"HD/P": "#f39c12",// Yellow Orange
				"WFH": "#3498db", // Blue
				"L": "#9b59b6",   // Purple
				"H": "#16a085",   // Teal
				"WO": "#7f8c8d",  // Grey
				"OD": "#2980b9",   // Blue
				"OS": "#8e44ad",   // Purple
				"OD": "#1abc9c",   // Turquoise
				"OS": "#000000",   // Black
			};

			const color = status_colors[data.status];
			if (color) {
				value = `<span style="font-weight:600;color:${color}">${data.status}</span>`;
			}
		}

		return value;
	},

	onload: function (report) {
		// Add legend only once
		if ($("#attendance-status-legend").length) return;

		const legend = `
			<div id="attendance-status-legend"
			     style="margin-bottom:10px; padding:6px; border:1px solid #d1d8dd; font-size:12px;">
				<span style="margin-left:10px; color:green;"><b>P</b></span> Present
				<span style="margin-left:20px; color:red;"><b>A</b></span> Absent
				<span style="margin-left:20px; color:orange;"><b>HD/A</b></span> Half Day/Other Half Absent
				<span style="margin-left:20px; color:#f39c12;"><b>HD/P</b></span> Half Day/Other Half Present
				<span style="margin-left:20px; color:#007bff;"><b>WFH</b></span> Work From Home
				<span style="margin-left:20px; color:#6f42c1;"><b>L</b></span> On Leave
				<span style="margin-left:20px; color:#198754;"><b>H</b></span> Holiday
				<span style="margin-left:20px; color:#6c757d;"><b>WO</b></span> Weekly Off
				<span style="margin-left:20px; color:#1abc9c;"><b>OD</b></span> On Duty
				<span style="margin-left:20px; color:#000000;"><b>OS</b></span> Off Shift
			</div>
		`;

		$(".page-form").after(legend);
	},
};

