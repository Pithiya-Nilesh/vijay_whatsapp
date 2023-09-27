import frappe
import requests
from frappe.utils.file_manager import save_file_on_filesystem, delete_file
from frappe.utils.pdf import get_pdf


def on_sales_order(doc, method):
    if doc.custom_whatsapp_no and doc.custom_send_whatsapp_message:
        if check_whatsapp_api():   
            file = create_and_store_file(doc)
            # file_url = frappe.utils.get_url()+file["file_url"]
            send_whatsapp_message([doc.custom_whatsapp_no, '918238875334'], 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])    


def on_sales_invoice(doc, method):
    if doc.custom_whatsapp_no and doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            print("\n\n yes in if \n\n")
        

def on_payment(doc, method):
    if doc.custom_whatsapp_no and doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            print("\n\n yes in if \n\n")


def on_purchase_order(doc, method):
    if doc.custom_whatsapp_no and doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            print("\n\n yes in if \n\n")


def send_whatsapp_message(numbers, message, file_url, filename):
    url, instance_id, access_token = get_whatsapp_credentials()
    print("in send whatsapp message")
    for number in numbers:
        # url = f"https://x3.woonotif.com/api/send.php?number={number}&type=text&message={message}&instance_id={instance_id}&access_token={access_token}"
        url = f"https://x3.woonotif.com/api/send.php?number={number}&type=media&message={message}&media_url={file_url}&instance_id={instance_id}&access_token={access_token}"
        response = requests.get(url)


def get_whatsapp_credentials():
    url = frappe.db.get_single_value("Whatsapp Settings", "url")
    instance_id = frappe.utils.password.get_decrypted_password("Whatsapp Settings", "Whatsapp Settings", "instance_id", raise_exception=False)
    access_token = frappe.utils.password.get_decrypted_password("Whatsapp Settings", "Whatsapp Settings", "access_token", raise_exception=False)
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