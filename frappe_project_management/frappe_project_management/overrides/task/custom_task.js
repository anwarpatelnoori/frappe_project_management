frappe.ui.form.on('Task', {
	refresh(frm) {
		// your code here
	},
    status: function (frm) {
        if (frm.doc.status == "Completed"){
            frm.set_value("completed_on",frappe.datetime.nowdate())
            frm.set_value("completed_by",frm.doc.custom_assigned_to)
        }
    }
})