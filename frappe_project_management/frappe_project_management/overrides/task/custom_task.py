import frappe
import requests
from erpnext.projects.doctype.task.task import Task

class CustomTask(Task):
    def after_insert(self):
        self.send_erp_aim()
    def send_erp_aim(self):
        try:
            erp_aim = frappe.get_doc("ERP Aim Settings","ERP Aim Settings")
            url = erp_aim.url + "/api/resource/ERP Aim"
            api_key = erp_aim.api_key
            api_secret = erp_aim.get_password("api_secret")
            headers = {
                "Authorization": f"token {api_key}:{api_secret}",
                "Content-Type": "application/json"
            }
            customer = frappe.db.get_value("Project", self.project, "customer")
            data = {
                "customer": customer,
                "subject": self.subject,
                "status": self.status,
                "progress_status": "Pending",
                "priority": self.priority,
                "description": self.description
            }
            response = requests.post(
                url, 
                json = data,
                headers = headers,
                timeout = 30
            )
            if response.status_code == 200:
                frappe.msgprint("ERP Aim is created in CubeZix ERP")
            else:
                frappe.msgprint(f"Sync failed. Status Code: {response.status_code}")
                frappe.log_error(title="ERP Aim Response",message=f"{response.status_code}\n{response.text}")

        except Exception:
            frappe.log_error(frappe.get_traceback(),"ERP Aim Task Sync")



