import frappe
from erpnext.projects.doctype.task.task import Task

class CustomTask(Task):
    def validate(self):
        frappe.msgprint("Validate")