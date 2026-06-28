frappe.query_reports["Unmarked Attendance Days"] = {
"filters": [
{
"fieldname": "from_date",
"label": "From Date",
"fieldtype": "Date",
"default": frappe.datetime.month_start(),
"reqd": 1
},
{
"fieldname": "to_date",
"label": "To Date",
"fieldtype": "Date",
"default": frappe.datetime.month_end(),
"reqd": 1
},
{
"fieldname": "department",
"label": "Department",
"fieldtype": "Link",
"options": "Department"
}
],
"datatable": {
"dynamicRowHeight": false
}
};

// delegated click handler bound once on document - works regardless of render hook availability
$(document).off("click", ".unmarked-count-link").on("click", ".unmarked-count-link", function(e) {
e.preventDefault();
const employee = $(this).data("employee");
const employee_name = $(this).data("employee-name");

const report_data = (frappe.query_report && frappe.query_report.data) || [];
const row = report_data.find(r => r.employee === employee);
if (!row) {
frappe.msgprint("Could not find data for this employee.");
return;
}

let dates = [];
try {
dates = JSON.parse(row.unmarked_dates_json || "[]");
} catch (err) {
dates = [];
}
const date_set = new Set(dates);

const months = {};
dates.forEach(d => {
const ym = d.substring(0, 7);
if (!months[ym]) months[ym] = [];
months[ym].push(d);
});

const month_names = ["January","February","March","April","May","June","July","August","September","October","November","December"];

let calendars_html = "";
Object.keys(months).sort().forEach(ym => {
const [year, month] = ym.split("-").map(Number);
const first_day = new Date(year, month - 1, 1);
const last_day = new Date(year, month, 0);
const start_weekday = first_day.getDay();
const days_in_month = last_day.getDate();
const month_name = month_names[month - 1];

let cells = "";
for (let i = 0; i < start_weekday; i++) {
cells += "<td></td>";
}
for (let day = 1; day <= days_in_month; day++) {
const iso = `${year}-${String(month).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
const is_unmarked = date_set.has(iso);
cells += `<td style="text-align:center; padding:6px; border-radius:4px;
${is_unmarked ? "background:#ffd1d1; color:#c0392b; font-weight:600;" : "color:#888;"}">${day}</td>`;
if ((start_weekday + day) % 7 === 0) cells += "</tr><tr>";
}

calendars_html += `
<div style="margin-bottom:18px;">
<div style="font-weight:600; margin-bottom:6px;">${month_name} ${year}</div>
<table style="width:100%; border-collapse:collapse; font-size:12px;">
<tr>
<td style="text-align:center; color:#999;">Su</td>
<td style="text-align:center; color:#999;">Mo</td>
<td style="text-align:center; color:#999;">Tu</td>
<td style="text-align:center; color:#999;">We</td>
<td style="text-align:center; color:#999;">Th</td>
<td style="text-align:center; color:#999;">Fr</td>
<td style="text-align:center; color:#999;">Sa</td>
</tr>
<tr>${cells}</tr>
</table>
</div>
`;
});

const d = new frappe.ui.Dialog({
title: `Unmarked Days — ${employee_name} (${dates.length} days)`,
size: "large",
fields: [
{
fieldtype: "HTML",
fieldname: "calendar_html",
options: `<div style="max-height:500px; overflow-y:auto; padding:5px;">${calendars_html}</div>`
}
]
});
d.show();
});
