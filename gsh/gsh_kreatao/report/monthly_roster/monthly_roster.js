
frappe.query_reports["Monthly Roster"] = {

    filters: [

        {
            fieldname: "filter_based_on",
            label: __("Filter Based On"),
            fieldtype: "Select",
            options: ["Month", "Date Range"],
            default: "Month",
            reqd: 1,
            on_change: function(report) {
                toggle_filters();
                auto_refresh(report);
            }
        },

        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Select",
            options: ["2025","2026","2027","2028","2029","2030","2031","2032","2033","2034","2035"],
            default: (new Date()).getFullYear().toString(),
            depends_on: "eval:doc.filter_based_on == 'Month'",
            on_change: function(report) {
                set_month_date_range();
                auto_refresh(report);
            }
        },

        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                "January","February","March","April","May","June",
                "July","August","September","October","November","December"
            ],
            default: (function() {
                const monthNames = [
                    "January","February","March","April","May","June",
                    "July","August","September","October","November","December"
                ];
                return monthNames[new Date().getMonth()];
            })(),
            depends_on: "eval:doc.filter_based_on == 'Month'",
            on_change: function(report) {
                set_month_date_range();
                auto_refresh(report);
            }
        },

        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            depends_on: "eval:doc.filter_based_on == 'Date Range'",
            on_change: function(report) {
                auto_refresh(report);
            }
        },

        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            depends_on: "eval:doc.filter_based_on == 'Date Range'",
            on_change: function(report) {
                auto_refresh(report);
            }
        },

        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            reqd: 1,
            default: frappe.defaults.get_user_default("Company"),
            on_change: function(report) {
                auto_refresh(report);
            }
        },

        {
            fieldname: "department",
            label: __("Department"),
            fieldtype: "Link",
            options: "Department",
            on_change: function(report) {
                auto_refresh(report);
            }
        }
    ],

    onload: function(report) {
        toggle_filters();
        set_month_date_range();
        report.refresh();
    }
};

// ===============================
// Toggle Required Fields
// ===============================
function toggle_filters() {

    let mode = frappe.query_report.get_filter_value("filter_based_on");

    let year = frappe.query_report.get_filter("year");
    let month = frappe.query_report.get_filter("month");
    let from_date = frappe.query_report.get_filter("from_date");
    let to_date = frappe.query_report.get_filter("to_date");

    if (mode === "Month") {
        year.df.reqd = 1;
        month.df.reqd = 1;
        from_date.df.reqd = 0;
        to_date.df.reqd = 0;
    } else {
        year.df.reqd = 0;
        month.df.reqd = 0;
        from_date.df.reqd = 1;
        to_date.df.reqd = 1;
    }

    year.refresh();
    month.refresh();
    from_date.refresh();
    to_date.refresh();
}


// ===============================
// Convert Month Name to Date
// ===============================
function set_month_date_range() {

    let mode = frappe.query_report.get_filter_value("filter_based_on");
    if (mode !== "Month") return;

    let year = frappe.query_report.get_filter_value("year");
    let month_name = frappe.query_report.get_filter_value("month");

    if (!year || !month_name) return;

    const monthNames = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ];

    let month_index = monthNames.indexOf(month_name);

    if (month_index === -1) return;

    let start_date = new Date(year, month_index, 1);
    let end_date = new Date(year, month_index + 1, 0);

    frappe.query_report.set_filter_value("from_date",
        frappe.datetime.obj_to_str(start_date));

    frappe.query_report.set_filter_value("to_date",
        frappe.datetime.obj_to_str(end_date));
}

//Auto refresh
function auto_refresh(report) {
    clearTimeout(report._refresh_timeout);

    report._refresh_timeout = setTimeout(() => {
        report.refresh();
    }, 300);  // small delay prevents multiple reloads
}