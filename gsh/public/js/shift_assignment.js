frappe.ui.form.on("Shift Assignment", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.page.btn_secondary.hide();  // hide default Cancel button

            frm.add_custom_button(__("Cancel"), function() {
                frappe.confirm(
                    "Are you sure you want to cancel this Shift Assignment? Linked attendance will also be cancelled.",
                    function() {
                        frappe.call({
                            method: "gsh.gsh_kreatao.custom_script.shift_assignment.force_cancel_shift_assignment",
                            args: { docname: frm.doc.name },
                            callback: function(r) {
                                if (!r.exc) {
                                    frappe.show_alert({ message: "Shift Assignment cancelled successfully.", indicator: "green" });
                                    frm.reload_doc();
                                }
                            }
                        });
                    }
                );
            }).addClass("btn-danger");
        }
    }
});
