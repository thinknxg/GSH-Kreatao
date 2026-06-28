frappe.query_reports["Staff Roster Report"] = {
filters: [
{
fieldname: "year",
label: __("Year"),
fieldtype: "Select",
options: (function () {
let y = new Date().getFullYear();
let opts = [];
for (let i = y - 3; i <= y + 1; i++) opts.push(String(i));
return opts.join("\n");
})(),
default: String(new Date().getFullYear()),
reqd: 1,
},
{
fieldname: "month",
label: __("Month"),
fieldtype: "Select",
options: [
{ value: "1",  label: __("January") },
{ value: "2",  label: __("February") },
{ value: "3",  label: __("March") },
{ value: "4",  label: __("April") },
{ value: "5",  label: __("May") },
{ value: "6",  label: __("June") },
{ value: "7",  label: __("July") },
{ value: "8",  label: __("August") },
{ value: "9",  label: __("September") },
{ value: "10", label: __("October") },
{ value: "11", label: __("November") },
{ value: "12", label: __("December") },
],
default: String(new Date().getMonth() + 1),
reqd: 1,
},
{
fieldname: "company",
label: __("Company"),
fieldtype: "Link",
options: "Company",
default: frappe.defaults.get_default("Company"),
},
{
fieldname: "department",
label: __("Department"),
fieldtype: "Link",
options: "Department",
},
{
fieldname: "employee",
label: __("Employee"),
fieldtype: "Link",
options: "Employee",
},
],

formatter: function (value, row, column, data, default_formatter) {
value = default_formatter(value, row, column, data);
if (!data) return value;

const raw = (data[column.fieldname] || "").toString().trim();

const styles = {
"P":   "color:#1a7d3a;background:#e6f9ed;font-weight:600",
"A":   "color:#c0392b;background:#fdecea;font-weight:600",
"H/D": "color:#e67e22;background:#fef5e7;font-weight:600",
"OL":  "color:#8e44ad;background:#f4ecf7;font-weight:600",
"WFH": "color:#2980b9;background:#eaf4fb;font-weight:600",
"WO":  "color:#1a5fa8;background:#eaf2ff;font-weight:600",
"NO":  "color:#6c3483;background:#f5eef8;font-weight:600",
"H":   "color:#117a65;background:#e8f8f5;font-weight:600",
"UM":  "color:#7f8c8d;background:#f2f3f4",
"NA":  "color:#e74c3c;background:#fdecea;font-weight:600",
};

if (styles[raw]) {
return `<span style="${styles[raw]};padding:2px 6px;border-radius:4px;">${raw}</span>`;
}
return value;
},
};
