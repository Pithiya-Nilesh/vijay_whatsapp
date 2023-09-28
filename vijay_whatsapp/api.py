import frappe
import requests
from frappe.utils.file_manager import save_file_on_filesystem, delete_file
from frappe.utils.pdf import get_pdf
from frappe.utils.password import get_decrypted_password
import json
from frappe import enqueue

@frappe.whitelist()
def on_sales_order(doc, method):
    if method == 'whitelist':
        doc = frappe.get_doc("Sales Order", doc)
    if doc.custom_whatsapp_no and doc.custom_send_whatsapp_message:
        if check_whatsapp_api():   
            file = create_and_store_file(doc)
            # file_url = frappe.utils.get_url()+file["file_url"]

            # '8238875334'
            whatsapp_no = [doc.custom_whatsapp_no]
            for sales_team in doc.sales_team:
                if sales_team.custom_whatsapp_no:
                    whatsapp_no.append(sales_team.custom_whatsapp_no)

            company = frappe.get_doc("Company", doc.company)
            for wpn in company.custom_whatsapp_no:
                if wpn.whatsapp_no and wpn.enable == 1:
                    whatsapp_no.append(wpn.whatsapp_no)

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your+Sales+Order+is+Created.', file_url=frappe.utils.get_url()+file["file_url"], filename=file["file_name"]) 


@frappe.whitelist()
def on_sales_invoice(doc, method):
    if method == 'whitelist':
        doc = frappe.get_doc("Sales Invoice", doc)
    if doc.custom_whatsapp_no and doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            print("\n\n yes in if \n\n")
        

@frappe.whitelist()
def on_payment(doc, method):
    if method == 'whitelist':
        doc = frappe.get_doc("Payment", doc)
    if doc.custom_whatsapp_no and doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            print("\n\n yes in if \n\n")


@frappe.whitelist()
def on_purchase_order(doc, method):
    if method == 'whitelist':
        doc = frappe.get_doc("Sales Order", doc)
    if doc.custom_whatsapp_no and doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            print("\n\n yes in if \n\n")


def send_whatsapp_message(numbers, message, file_url, filename):
    url, instance_id, access_token = get_whatsapp_credentials()
    print("in send whatsapp message")
    for number in numbers:
        url = f"https://x3.woonotif.com/api/send.php?number={number}&type=text&message={message}&instance_id={instance_id}&access_token={access_token}"
        # url = f"https://x3.woonotif.com/api/send.php?number=91{number}&type=media&message={message}&media_url={file_url}&instance_id={instance_id}&access_token={access_token}"
        response = requests.get(url)

        print("\n\n response", response, "\n\n")
        print("\n\n response", response.text, "\n\n")

def get_whatsapp_credentials():
    url = frappe.db.get_single_value("Whatsapp Settings", "url")
    instance_id = get_decrypted_password("Whatsapp Settings", "Whatsapp Settings", "instance_id", raise_exception=False)
    access_token = get_decrypted_password("Whatsapp Settings", "Whatsapp Settings", "access_token", raise_exception=False)
    return url, instance_id, access_token


def check_whatsapp_api():
    enable = frappe.db.get_single_value("Whatsapp Settings", "enable")
    if enable == 0:
        frappe.msgprint("Please Enable WhatsApp Api in Whatsapp Settings To Send Whatsapp Message.")
        return False
    else:
        return True
    

def create_and_store_file(doc):
    from frappe.utils import today

    html_content = frappe.get_print(doc.doctype, doc.name)
    pdf_content = get_pdf(html_content) 
    pdf_file_name = f"Sales_Order_{doc.name}.pdf"

    file = save_file_on_filesystem(pdf_file_name, pdf_content)

    doc = frappe.get_doc({
        'doctype': 'Sent File',
        'file_path': file["file_url"],
        'sent_date': today()
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return file


@frappe.whitelist(allow_guest=True)    
def delete_sent_file():

    from datetime import datetime # from python std library
    from frappe.utils import add_to_date

    before_14_days = add_to_date(datetime.now(), days=-14, as_string=True)
    doc_name = frappe.db.get_list("Sent File", filters=[["sent_date", "<", before_14_days]], fields=["name", "file_path"])
    for name in doc_name:
        delete_file(name.file_path)
        frappe.delete_doc('Sent File', name.name)
        frappe.db.commit()