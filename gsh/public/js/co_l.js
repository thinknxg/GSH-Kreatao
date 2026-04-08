frappe.listview_settings['Compensatory Off'].onload = function(listview) {
    // add button to menu
    listview.page.add_action_item(__("Test option"), function() {
    	test( listview );
});
};

function test( listview )
{
	let names=[];
	$.each(listview.get_checked_items(), function(key, value) {
		names.push(value.name);
	});
	if (names.length === 0) {
		frappe.throw(__("No rows selected."));
	}
			
	frappe.msgprint( names );
}