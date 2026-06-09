import frappe
import requests
from erpnext.projects.doctype.task.task import Task
from frappe.utils.password import get_decrypted_password

class CustomTask(Task):
    def after_insert(self):
        self.create_erp_aim()
    
    def before_save(self):
        if not self.is_new():
            self.update_erp_aim()
            if not self.exp_end_date:
                frappe.msgprint("Expeceted End Date of Task is Missing")
    def cubezix_api_details(self):
        try:
            erp_aim = frappe.get_doc("ERP Aim Settings","ERP Aim Settings")
            url = erp_aim.url + "/api/resource"
            api_key = erp_aim.api_key
            api_secret = erp_aim.get_password("api_secret")
            headers = {
                "Authorization": f"token {api_key}:{api_secret}",
                "Content-Type": "application/json"
            }

            # Get user specif api
            for i in erp_aim.developers_api:
                if i.user == frappe.session.user and i.enabled == 1:
                    api_key = i.api_key
                    api_secret = get_decrypted_password("Developers API", i.name, "api_secret")
                    headers = {
                    "Authorization": f"token {api_key}:{api_secret}",
                    "Content-Type": "application/json"
                    }
                    break
            return url, api_key, api_secret, headers
        except Exception:
                frappe.log_error(title = "Invaild ERP Aim Token", message=str(Exception))

    
    def create_erp_aim(self):
        try:
            url, api_key, api_secret, headers = self.cubezix_api_details()
            create_doc_url = url + "/ERP Aim"
            customer = frappe.db.get_value("Project", self.project, "customer")
            custom_assigned_to_full_name = frappe.db.get_value("User",self.custom_assigned_to, "full_name")
            data = {
                "customer": customer,
                "subject": self.subject,
                "status": self.status,
                "progress_status": "Pending",
                "priority": self.priority,
                "description": self.description,
                "assigned_too": custom_assigned_to_full_name,
                "due_date": self.exp_end_date
            }
            response = requests.post(
                create_doc_url, 
                json = data,
                headers = headers,
                timeout = 30
            )
            if response.status_code == 200:
                response_json = response.json()
                if "data" in response_json and "name" in response_json["data"]:
                    erp_aim_id = "https://erp.cubezix.com/app/erp-aim/" + response_json["data"]["name"]
                    frappe.db.set_value("Task", self.name, "custom_erp_aim", erp_aim_id)
                    
                frappe.msgprint("ERP Aim is created in CubeZix ERP")
            else:
                frappe.msgprint(f"Sync failed. Status Code: {response.status_code}")
                frappe.log_error(title="ERP Aim Response",message=f"{response.status_code}\n{response.text}")

        except Exception:
            frappe.log_error(frappe.get_traceback(),"ERP Aim Task Sync")

    def update_erp_aim(self):
        if self.has_value_changed("description"):
            self.send_update_request("description", self.description)
        if self.has_value_changed("custom_assigned_to"):
            custom_assigned_to_full_name = frappe.db.get_value("User",self.custom_assigned_to, "full_name")
            self.send_update_request("assigned_too", custom_assigned_to_full_name)
        if self.has_value_changed("status"):
            self.send_update_request("status", self.status)
        if self.has_value_changed("priority"):
            self.send_update_request("priority", self.priority)
        if self.has_value_changed("exp_end_date"):
            self.send_update_request("due_date", self.exp_end_date)
    

    def send_update_request(self, field_name, field_value):
        url, api_key, api_secret, headers = self.cubezix_api_details()
        erp_aim_id = self.custom_erp_aim.split("/")[-1]
        update_doc_url = f'{url}/ERP Aim/{erp_aim_id}'
        data = {
            "doctype": "ERP Aim",
            "name": erp_aim_id,
            field_name: field_value
        }
        if field_name == "status" and field_value == "Completed":
            data["closure_comments"] = self.custom_closure_comments
            data["resolved_on"] =  str(frappe.utils.now_datetime())
        try:
            response = requests.put(update_doc_url, json = data, headers = headers, timeout = 30)
            if response.status_code != 200:
                frappe.msgprint(f"Sync failed. Status Code: {response.status_code}")
                frappe.log_error(title="ERP Aim Response",message=f"{response.status_code}\n{response.text}")
        except Exception:
            frappe.log_error(title = f"ERP Aim Update Failed: {self.custom_erp_aim}", message = frappe.get_traceback())

                





