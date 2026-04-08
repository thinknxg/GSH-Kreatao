// Copyright (c) 2025, Rawas and contributors
// For license information, please see license.txt

frappe.ui.form.on("Experience Certificate", {
	refresh(frm) {

	},
    after_save: function(frm) {
        // frm.save()
        if (!frm.is_new()) {
            // Example dynamic values
            let re_number = frm.doc.name || "GMIS/2025/HR/144";
            let certificate_date = frm.doc.posting_date || frappe.datetime.get_today(); // dynamic date
            // Format date to DD/MM/YYYY
            let parts = certificate_date.split("-");
            let formatted_date = parts[2] + "/" + parts[1] + "/" + parts[0];
            // Set default for content_1 if empty
            if (!frm.doc.content_1) {
                frm.set_value("content_1", `
                    <p><b>Re Number: ${re_number}</b></p>
                    <p><b>Date: ${formatted_date}</b></p><br><br>
                    <h4 style="text-align:center;"><u><b>EXPERIENCE CERTIFICATE</b></u></h4>
                `);
            }
    
            // Set default for content_2 if empty
            if (!frm.doc.content_2) {
                frm.set_value("content_2", `
                    <div style="text-align: justify;">
                        <p>This is to certify that the above-mentioned employee was employed with Gulf Specialized Hospital, in the capacity of the position mentioned above. 
                        During the above-mentioned period, he/she carried out assigned duties and responsibilities in accordance with the policies and standards of the organization.</p>

                        <p><b>Office Address:</b> Gulf Specialized Hospital, Maktabi Building, Al Rumaila street Al Wattaya, Muscat-Sultanate of Oman</p>

                        <p>Gulf Specialized Hospital is a multispecialty hospital located in Muscat, Sultanate of Oman. With more than 20 medical & surgical specialties including, 
                        orthopedic, neurology, cardiology, bariatric, urology, general surgery, plastic surgery, gastroenterology & others, GSH aims to be the optimal healthcare choice.</p>

                        <p>This certificate is issued at the request of the employee without any liability or commitment on the part of Gulf Medical Integrated Services L.L.C toward any third party whatsoever.</p><br><br>

                        <p><b>Your Sincerely,</b></p><br><br>
                        <p><b>Zuhair Al Abduwani<br>CEO</b></p>
                    </div>
                `);
            }
        }
        frm.save()
    },
});
