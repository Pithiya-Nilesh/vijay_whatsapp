import frappe
import requests
from frappe.utils.file_manager import save_file_on_filesystem, delete_file
from frappe.utils.pdf import get_pdf
from frappe.utils.password import get_decrypted_password
from frappe.utils import get_url
import json
from frappe import enqueue

@frappe.whitelist()
def on_sales_order(doc, method):
    '''
        for send whatsapp notification map whatsapp number and create file on sales order doctype
    '''
    if method == 'whitelist':
        doc = frappe.get_doc("Sales Order", doc)
    if doc.contact_mobile and doc.custom_send_whatsapp_message:
        if check_whatsapp_api():   
            file = create_and_store_file(doc)
            # file_url = frappe.utils.get_url()+file["file_url"]

            # '8238875334'
            whatsapp_no = [doc.contact_mobile]
            for sales_team in doc.sales_team:
                if sales_team.custom_whatsapp_no:
                    whatsapp_no.append(sales_team.custom_whatsapp_no)

            company = frappe.get_doc("Company", doc.company)
            for wpn in company.custom_whatsapp_no:
                if wpn.whatsapp_no and wpn.enable == 1:
                    if wpn.whatsapp_no not in whatsapp_no:
                        whatsapp_no.append(wpn.whatsapp_no)

            file_url = f"{get_url()+file['file_url']}"
            # file_url = 'https://vijaymamra.frappe.cloud/files/Payment%20Entry-ACC-PAY-2023-00002.pdf'

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your+Sales+Order+is+Created.', file_url=file_url, filename=file['file_name'], docname=doc.name) 
            # enqueue("vijay_whatsapp.api.set_whatsapp_log", doctype="Sales Order", docname=doc.name, whatsapp_no=whatsapp_no, response=response)


@frappe.whitelist()
def on_sales_invoice(doc, method):
    '''
        for send whatsapp notification map whatsapp number and create file on sales invoice doctype
    '''
    if method == 'whitelist':
        doc = frappe.get_doc("Sales Invoice", doc)
    if doc.contact_mobile and doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            file = create_and_store_file(doc)
            # file_url = frappe.utils.get_url()+file["file_url"]

            # '8238875334'
            whatsapp_no = [doc.contact_mobile]
            for sales_team in doc.sales_team:
                if sales_team.custom_whatsapp_no:
                    if sales_team.custom_whatsapp_no not in whatsapp_no:
                        whatsapp_no.append(sales_team.custom_whatsapp_no)

            company = frappe.get_doc("Company", doc.company)
            for wpn in company.custom_whatsapp_no:
                if wpn.whatsapp_no and wpn.enable == 1:
                    whatsapp_no.append(wpn.whatsapp_no)

            file_url = f"{get_url()+file['file_url']}"

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your+Sales+Invoice+is+Created.', file_url=file_url, filename=file['file_name']) 


@frappe.whitelist()
def on_outstanding_sales_invoice_reminder():
    '''
        send auto outstanding sales invoice reminder.
    '''
    from frappe.utils import today

    if check_scheduler_is_enable():
        if check_whatsapp_api():
            data = frappe.db.get_list("Sales Invoice", filters={"due_date": '2023-10-29', "custom_send_whatsapp_message": 1, "status": ["Overdue", "Unpaid"], "contact_mobile": ("!=", '')}, fields=['name'])

            for name in data:
                doc = frappe.get_doc("Sales Invoice", name.name)
                if doc.contact_mobile:
                    # file = enqueue('vijay_whatsapp.api.create_and_store_file', doc=doc)

                    file = create_and_store_file(doc)
                    
                    whatsapp_no = [doc.contact_mobile]
                    for sales_team in doc.sales_team:
                        if sales_team.custom_whatsapp_no:
                            if sales_team.custom_whatsapp_no not in whatsapp_no:
                                whatsapp_no.append(sales_team.custom_whatsapp_no)

                    company = frappe.get_doc("Company", doc.company)
                    for wpn in company.custom_whatsapp_no:
                        if wpn.whatsapp_no and wpn.enable == 1:
                            whatsapp_no.append(wpn.whatsapp_no)

                    file_url = f"{get_url()+file['file_url']}"

                    # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
                    enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your+Sales+Invoice+is+Created.', file_url=file_url, filename=file['file_name']) 


@frappe.whitelist()
def on_payment_entry(doc, method):
    '''
        for send whatsapp notification map whatsapp number and create file on payment doctype
    '''
    if method == 'whitelist':
        doc = frappe.get_doc("Payment Entry", doc)
    if doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            file = create_and_store_file(doc)

            whatsapp_no = []
            for payment_team in doc.custom_whatsapp_no:
                if payment_team.whatsapp_no and payment_team.enable == 1:
                    whatsapp_no.append(payment_team.whatsapp_no)

            company = frappe.get_doc("Company", doc.company)
            for wpn in company.custom_whatsapp_no:
                if wpn.whatsapp_no and wpn.enable == 1:
                    if wpn.whatsapp_no not in whatsapp_no:
                        whatsapp_no.append(wpn.whatsapp_no)

            message = ''
            if doc.payment_type == 'Receive':
                message = f'Payment Received From {doc.party_name}.'
            if doc.payment_type == 'Pay':
                message = f'Payment Paid To {doc.party_name}'
            if doc.payment_type == 'Internal Transfer':
                message = f'Internal Payment Entry From {doc.paid_from} To {doc.paid_to}.'

            file_url = f"{get_url()+file['file_url']}"

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message=message, file_url=file_url, filename=file['file_name']) 


@frappe.whitelist()
def on_purchase_order(doc, method):
    '''
        for send whatsapp notification map whatsapp number and create file on purchase doctype
    '''
    if method == 'whitelist':
        doc = frappe.get_doc("Purchase Order", doc)
    if doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            file = create_and_store_file(doc)

            whatsapp_no = []
            for purchase_team in doc.custom_whatsapp_no:
                if purchase_team.whatsapp_no and purchase_team.enable == 1:
                    whatsapp_no.append(purchase_team.whatsapp_no)

            company = frappe.get_doc("Company", doc.company)
            for wpn in company.custom_whatsapp_no:
                if wpn.whatsapp_no and wpn.enable == 1:
                    if wpn.whatsapp_no not in whatsapp_no:
                        whatsapp_no.append(wpn.whatsapp_no)

            file_url = f"{get_url()+file['file_url']}"

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your+Purchase+Order+is+Created.', file_url=file_url, filename=file['file_name']) 


@frappe.whitelist()
def on_delivery_note(doc, method):
    '''
        for send whatsapp notification map whatsapp number and create file on delivery note doctype
    '''
    if method == 'whitelist':
        doc = frappe.get_doc("Delivery Note", doc)
    if doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            file = create_and_store_file(doc)

            whatsapp_no = [doc.contact_mobile]
            for delivery_team in doc.custom_whatsapp_no:
                if delivery_team.whatsapp_no and delivery_team.enable == 1:
                    whatsapp_no.append(delivery_team.whatsapp_no)

            company = frappe.get_doc("Company", doc.company)
            for wpn in company.custom_whatsapp_no:
                if wpn.whatsapp_no and wpn.enable == 1:
                    if wpn.whatsapp_no not in whatsapp_no:
                        whatsapp_no.append(wpn.whatsapp_no)

            file_url = f"{get_url()+file['file_url']}"

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your+order+has+been+dispatched.', file_url=file_url, filename=file['file_name']) 

            
def send_whatsapp_message(numbers, message, file_url, filename, docname):
    '''
        send whatsapp message with file.
    '''

    url, instance_id, access_token = get_whatsapp_credentials()
    # print("in send whatsapp message")
    for number in numbers:
        # url = f"https://x3.woonotif.com/api/send.php?number=91{number}&type=text&message={message}&instance_id={instance_id}&access_token={access_token}"
        url = f"https://x3.woonotif.com/api/send.php?number=91{number}&type=media&message={message}&media_url={file_url}&instance_id={instance_id}&access_token={access_token}"
        
        # print("\n\n url", url, "\n\n")
        response = requests.get(url)

        enqueue("vijay_whatsapp.api.set_whatsapp_log", doctype="Sales Order", docname=docname, whatsapp_no=number, response=json.loads(response.text))

        # return response


def get_whatsapp_credentials():
    '''
        get whatsapp decrypted credentials from whatsapp setting.
    '''
    url = frappe.db.get_single_value("Whatsapp Settings", "url")
    instance_id = get_decrypted_password("Whatsapp Settings", "Whatsapp Settings", "instance_id", raise_exception=False)
    access_token = get_decrypted_password("Whatsapp Settings", "Whatsapp Settings", "access_token", raise_exception=False)
    # print("\n\n instance id", instance_id)
    # print("\n\n access token", access_token)
    return url, instance_id, access_token


def check_whatsapp_api():
    '''
        check whatsapp api is enable.
    '''
    enable = frappe.db.get_single_value("Whatsapp Settings", "enable")
    if enable == 0:
        frappe.msgprint("Please Enable WhatsApp Api in Whatsapp Settings To Send Whatsapp Message.")
        return False
    else:
        return True
    

def check_scheduler_is_enable():
    '''
        check scheduler is enable.
    '''
    enable = frappe.db.get_single_value("Whatsapp Settings", "enable_scheduler")
    if enable == 0:
        return False
    else:
        return True


def create_and_store_file(doc):
    '''
        get doctype html and convert to pdf and store in public file and store path in sent file doctype.
    '''
    from frappe.utils import today

    html_content = frappe.get_print(doc.doctype, doc.name)
    pdf_content = get_pdf(html_content) 
    pdf_file_name = f"{doc.doctype}-{doc.name}.pdf"

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
def set_whatsapp_log(doctype, docname, whatsapp_no, response):
    '''
        set whatsapp log after message send
    '''
    # create a new e-invoice log
    doc = frappe.new_doc('Whatsapp Log')
    doc.w_doctype = doctype
    doc.w_docname = docname
    doc.whatsapp_no = whatsapp_no
    doc.response = json.dumps(response, indent=4)
    doc.insert()
    frappe.db.commit()


@frappe.whitelist(allow_guest=True)    
def delete_sent_file():
    '''
        this function delete old file created so no space take in system.
    '''
    from datetime import datetime # from python std library
    from frappe.utils import add_to_date

    before_14_days = add_to_date(datetime.now(), days=-14, as_string=True)
    doc_name = frappe.db.get_list("Sent File", filters=[["sent_date", "<", before_14_days]], fields=["name", "file_path"])
    for name in doc_name:
        delete_file(name.file_path)
        frappe.delete_doc('Sent File', name.name)
        frappe.db.commit()


@frappe.whitelist()
def get_mobile_numbers(roles):

    roles = json.loads(roles)

    final_list = []
    # Query to fetch mobile numbers of users with the specified role
    users = frappe.get_all('User', filters={'role': ['in', roles]}, fields=['first_name', 'mobile_no'])

    for user in users:
        if user.mobile_no:
            if user not in final_list:
                final_list.append(user)
    return final_list
