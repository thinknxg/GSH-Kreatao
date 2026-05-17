// Copyright (c) 2025, Rawas and contributors
// For license information, please see license.txt
frappe.ui.form.on("Employment Certificate", {
    refresh(frm) {
    },
    after_save: function(frm) {
        if (!frm.is_new()) {
            let re_number = frm.doc.name || "HMIS/2025/HR/139";
            let certificate_date = frm.doc.posting_date || frappe.datetime.get_today();
            let parts = certificate_date.split("-");
            let formatted_date = parts[2] + "/" + parts[1] + "/" + parts[0];
            if (!frm.doc.content_1) {
                frm.set_value("content_1", `<p style="margin:0;padding:0;"><b>Re Number: ${re_number}</b></p><p style="margin:0;padding:0;"><b>Date: ${formatted_date}</b></p><br><p style="text-align:center;margin:0;padding:0;"><u><b>EMPLOYMENT CERTIFICATE</b></u></p>`);
            }
            if (!frm.doc.content_2) {
                frm.set_value("content_2", `<div style="text-align: justify;"><p>This is to certify that the above-mentioned employee is employed with Gulf Specialized Hospital, in the position mentioned above.</p><p>Gulf Specialized Hospital is a multispecialty hospital located in Muscat, Sultanate of Oman. With more than 20 medical & surgical specialties including, orthopedic, neurology, cardiology, bariatric, urology, general surgery, plastic surgery, gastroenterology & others, GSH aims to be the optimal healthcare choice.</p><p>This certificate has been issued at the request of the employee without any liability or commitment on the part of Gulf Medical Integrated Services L.L.C toward any third party whatsoever.</p><p><b>"The validity of the certificate shall be one month from the date of issue."</b></p><br><br><p><b>Your Sincerely,</b></p><br><br><p><b>Zuhair Al Abduwani<br>CEO</b></p></div>`);
            }
        }
        frm.save()
    },
});
