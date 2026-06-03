import frappe
from erpnext.projects.doctype.task.task import Task

class CustomTask(Task):
    def validate(self):
        pass
        frappe.msgprint("Validate")