import frappe
from frappe.core.doctype.access_log.access_log import make_access_log
from frappe.utils.data import today
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
            # file = create_and_store_file(doc)
            # file_url = frappe.utils.get_url()+file["file_url"]

            whatsapp_no = [doc.contact_mobile]            
            for sales_team in doc.sales_team:
                if sales_team.custom_whatsapp_no:
                    whatsapp_no.append(sales_team.custom_whatsapp_no)

            if doc.sales_partner:
                sp_doc_name = frappe.db.sql(" select parent from `tabDynamic Link` where link_name=%s ", (doc.sales_partner), as_dict=True)
                if sp_doc_name:
                    sp_number = frappe.db.sql(" select phone from `tabContact` where name=%s ", (sp_doc_name[0]['parent']), as_dict=True)
                    if sp_number:
                        whatsapp_no.append(sp_number[0]['phone'])

            company = frappe.get_doc("Company", doc.company)
            for wpn in company.custom_whatsapp_no:
                if wpn.whatsapp_no and wpn.enable == 1:
                    if wpn.whatsapp_no not in whatsapp_no:
                        whatsapp_no.append(wpn.whatsapp_no)

            # find_link = frappe.db.get_value("Dynamic Link", filters={"link_name": company.name}, fieldname=["parent"])
            # address = frappe.db.get_value("Address", find_link, fieldname=['*'], as_dict=True)

            
            # message = f"Your+Sales+Order+is+Created for {company.name}. address:- {address['address_line1'], address['address_line2'] - address['pincode'], address['city'], address['state'], address['county'], address['email_id'], address['email_id'], address['phone']}"
            message = "Your+Sales+Order+is+Created"
            enqueue('vijay_whatsapp.api.create_and_store_file', doc=doc, whatsapp_no=whatsapp_no, message=message)

            # file_url = f"{get_url()+file['file_url']}"
            # file_url = 'https://vijaymamra.frappe.cloud/files/Payment%20Entry-ACC-PAY-2023-00002.pdf'

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            # enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your+Sales+Order+is+Created.', file_url=file_url, filename=file['file_name'], docname=doc.name) 
            # enqueue("vijay_whatsapp.api.set_whatsapp_log", doctype="Sales Order", docname=doc.name, whatsapp_no=whatsapp_no, response=response)


@frappe.whitelist()
def on_sales_invoice(doc, method):
    print("this calllllll")
    '''
        for send whatsapp notification map whatsapp number and create file on sales invoice doctype
    '''
    if method == 'whitelist':
        doc = frappe.get_doc("Sales Invoice", doc)
    if doc.contact_mobile and doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            # file = create_and_store_file(doc)
            # file_url = frappe.utils.get_url()+file["file_url"]

            
            whatsapp_no = [doc.contact_mobile]
            for sales_team in doc.sales_team:
                if sales_team.custom_whatsapp_no:
                    if sales_team.custom_whatsapp_no not in whatsapp_no:
                        whatsapp_no.append(sales_team.custom_whatsapp_no)
            if doc.sales_partner:
                sp_doc_name = frappe.db.sql(" select parent from `tabDynamic Link` where link_name=%s ", (doc.sales_partner), as_dict=True)
                if sp_doc_name:
                    sp_number = frappe.db.sql(" select phone from `tabContact` where name=%s ", (sp_doc_name[0]['parent']), as_dict=True)
                    if sp_number:
                        whatsapp_no.append(sp_number[0]['phone'])


            company = frappe.get_doc("Company", doc.company)
            for wpn in company.custom_whatsapp_no:
                if wpn.whatsapp_no and wpn.enable == 1:
                    whatsapp_no.append(wpn.whatsapp_no)
            
            message = 'Your+Sales+Invoice+is+Created.'

            enqueue('vijay_whatsapp.api.create_and_store_file', doc=doc, whatsapp_no=whatsapp_no, message=message)

            # file_url = f"{get_url()+file['file_url']}"

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            # enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your+Sales+Invoice+is+Created.', file_url=file_url, filename=file['file_name'], docname=doc.name) 


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
                    enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your+Sales+Invoice+is+Outstanding.', file_url=file_url, filename=file['file_name'], docname=doc.name) 


@frappe.whitelist()
def on_payment_entry(doc, method):
    '''
        for send whatsapp notification map whatsapp number and create file on payment doctype
    '''
    if method == 'whitelist':
        doc = frappe.get_doc("Payment Entry", doc)
    if doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            # file = create_and_store_file(doc)

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

            enqueue('vijay_whatsapp.api.create_and_store_file', doc=doc, whatsapp_no=whatsapp_no, message=message)
            # file_url = f"{get_url()+file['file_url']}"

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            # enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message=message, file_url=file_url, filename=file['file_name'], docname=doc.name) 


@frappe.whitelist()
def on_purchase_order(doc, method):
    '''
        for send whatsapp notification map whatsapp number and create file on purchase doctype
    '''
    if method == 'whitelist':
        doc = frappe.get_doc("Purchase Order", doc)
    if doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            # file = create_and_store_file(doc)

            whatsapp_no = []
            for purchase_team in doc.custom_whatsapp_no:
                if purchase_team.whatsapp_no and purchase_team.enable == 1:
                    whatsapp_no.append(purchase_team.whatsapp_no)

            company = frappe.get_doc("Company", doc.company)
            for wpn in company.custom_whatsapp_no:
                if wpn.whatsapp_no and wpn.enable == 1:
                    if wpn.whatsapp_no not in whatsapp_no:
                        whatsapp_no.append(wpn.whatsapp_no)

            message = 'Your+Purchase+Order+is+Created.'

            enqueue('vijay_whatsapp.api.create_and_store_file', doc=doc, whatsapp_no=whatsapp_no, message=message)

            # file_url = f"{get_url()+file['file_url']}"

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            # enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your+Purchase+Order+is+Created.', file_url=file_url, filename=file['file_name'], docname=doc.name) 


@frappe.whitelist()
def on_delivery_note(doc, method):
    '''
        for send whatsapp notification map whatsapp number and create file on delivery note doctype
    '''
    if method == 'whitelist':
        doc = frappe.get_doc("Delivery Note", doc)
    if doc.custom_send_whatsapp_message:
        if check_whatsapp_api():
            # file = create_and_store_file(doc)

            whatsapp_no = [doc.contact_mobile]
            for delivery_team in doc.custom_whatsapp_no:
                if delivery_team.whatsapp_no and delivery_team.enable == 1:
                    whatsapp_no.append(delivery_team.whatsapp_no)

            company = frappe.get_doc("Company", doc.company)
            for wpn in company.custom_whatsapp_no:
                if wpn.whatsapp_no and wpn.enable == 1:
                    if wpn.whatsapp_no not in whatsapp_no:
                        whatsapp_no.append(wpn.whatsapp_no)

            message = 'Your+order+has+been+dispatched.'

            enqueue('vijay_whatsapp.api.create_and_store_file', doc=doc, whatsapp_no=whatsapp_no, message=message)

            # file_url = f"{get_url()+file['file_url']}"

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            # enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your+order+has+been+dispatched.', file_url=file_url, filename=file['file_name'], docname=doc.name) 



@frappe.whitelist()
def on_customer_receivable(name):
    file = send_report_pdf(name, "R")
    doc = frappe.get_doc("Customer", name)
    if doc.mobile_no:
        if check_whatsapp_api():   
            whatsapp_no = [doc.mobile_no]

            company = frappe.get_doc("Company", "Vijay Mamra Private Limited")
            for wpn in company.custom_whatsapp_no:
                if wpn.whatsapp_no and wpn.enable == 1:
                    if wpn.whatsapp_no not in whatsapp_no:
                        whatsapp_no.append(wpn.whatsapp_no)

            file_url = f"{get_url()+file['file_url']}"
            # file_url = 'https://vijaymamra.frappe.cloud/files/Payment%20Entry-ACC-PAY-2023-00002.pdf'

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your OutStanding Invoice Details', file_url=file_url, filename=file['file_name'], docname=doc.name, doctype=doc.doctype) 
            # enqueue("vijay_whatsapp.api.set_whatsapp_log", doctype="Sales Order", docname=doc.name, whatsapp_no=whatsapp_no, response=response)


@frappe.whitelist()
def on_customer_general_ledger(name):
    file = send_report_pdf(name, "G")
    doc = frappe.get_doc("Customer", name)
    if doc.mobile_no:
        if check_whatsapp_api():   
            whatsapp_no = [doc.mobile_no]

            company = frappe.get_doc("Company", "Vijay Mamra Private Limited")
            for wpn in company.custom_whatsapp_no:
                if wpn.whatsapp_no and wpn.enable == 1:
                    if wpn.whatsapp_no not in whatsapp_no:
                        whatsapp_no.append(wpn.whatsapp_no)

            file_url = f"{get_url()+file['file_url']}"
            # file_url = 'https://vijaymamra.frappe.cloud/files/Payment%20Entry-ACC-PAY-2023-00002.pdf'

            # send_whatsapp_message(whatsapp_no, 'Your+Sales+Order+is+Created.', frappe.utils.get_url()+file["file_url"], file["file_name"])
            enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message='Your OutStanding Invoice Details', file_url=file_url, filename=file['file_name'], docname=doc.name, doctype=doc.doctype) 
            # enqueue("vijay_whatsapp.api.set_whatsapp_log", doctype="Sales Order", docname=doc.name, whatsapp_no=whatsapp_no, response=response)


def send_whatsapp_message(numbers, message, file_url, filename, docname, doctype):
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
        owner = frappe.session.user
        data = json.loads(response.text)
        
        if "status" in data and data["status"] == "success":
            enqueue('vijay_whatsapp.api.set_comment', doctype=doctype, docname=docname, owner=owner, content="<div class='card'><b style='color: green' class='px-2 pt-2'>Whatsapp Message Sent: </b> <span class='px-2 pb-2'>Your whatsapp message send successfully.</span></div>")
            enqueue("vijay_whatsapp.api.set_whatsapp_log", doctype=doctype, docname=docname, whatsapp_no=number, response=json.loads(response.text), status="Sent")
        else:
            enqueue('vijay_whatsapp.api.set_comment', doctype=doctype, docname=docname, owner=owner, content=f"<div class='card'><b style='color: red' class='px-2 pt-2'>Whatsapp Message Not Sent: </b> <span class='px-2 pb-2'>{response.text}</span></div>")
            enqueue("vijay_whatsapp.api.set_whatsapp_log", doctype=doctype, docname=docname, whatsapp_no=number, response=json.loads(response.text), status="Failed")

    return response


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


def create_and_store_file(doc, whatsapp_no, message):
    '''
        get doctype html and convert to pdf and store in public file and store path in sent file doctype.
    '''
    from frappe.utils import today

    if doc.doctype == "Sales Order":
        html_content = frappe.get_print(doc.doctype, doc.name, 'Sales Order Print Designer')
    elif doc.doctype == "Sales Invoice":
        html_content = frappe.get_print(doc.doctype, doc.name, 'New Invoice' )
    pdf_content = get_pdf(html_content) 
    pdf_file_name = f"{doc.doctype}-{doc.name}.pdf"

    file = save_file_on_filesystem(pdf_file_name, pdf_content)

    sent_file = frappe.get_doc({
        'doctype': 'Sent File',
        'file_path': file["file_url"],
        'sent_date': today()
    })
    sent_file.insert(ignore_permissions=True)
    frappe.db.commit()
    
    # return file
    file_url = f"{get_url()+file['file_url']}"
    enqueue('vijay_whatsapp.api.send_whatsapp_message', numbers=whatsapp_no, message=message, file_url=file_url, filename=file['file_name'], docname=doc.name, doctype=doc.doctype)


@frappe.whitelist(allow_guest=True)
def set_whatsapp_log(doctype, docname, whatsapp_no, response, status):
    '''
        set whatsapp log after message send
    '''
    # create a new e-invoice log
    doc = frappe.new_doc('Whatsapp Log')
    doc.w_doctype = doctype
    doc.w_docname = docname
    doc.whatsapp_no = whatsapp_no
    doc.status = status
    doc.response = json.dumps(response, indent=4)
    doc.insert()
    frappe.db.commit()


def set_comment(doctype, docname, owner, content):
    activity = frappe.get_doc(
        {"doctype": "Comment", "comment_type": "Info",
         "reference_doctype": doctype, "reference_name": docname,
         "content": content})
    activity.insert(ignore_permissions=True)
    frappe.db.commit()

    comment = frappe.get_last_doc('Comment')
    frappe.db.set_value('Comment', f'{comment.name}', {"owner": owner})
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


@frappe.whitelist()
def send_report_pdf(name, report_name):
    from vijay_whatsapp.report import get_receivable_report_content, get_general_report_content
    if report_name == "R":
        pdf_content = get_pdf(get_receivable_report_content(name)) 
        pdf_file_name = f"Receivable-{name}.pdf"
    
    if report_name == "G":
        pdf_content = get_pdf(get_general_report_content(name)) 
        pdf_file_name = f"General Ledger-{name}.pdf"

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
def check(numbers='', message='', file_url=''):
    # '''
    #     send whatsapp message with file.
    # '''
    # file_url = 'https://vijaymamra.frappe.cloud/files/Payment%20Entry-ACC-PAY-2023-00002.pdf'
    # message = 'asdf'

    # url, instance_id, access_token = get_whatsapp_credentials()
    # # print("in send whatsapp message")
    # number = 7990915950
    # # url = f"https://x3.woonotif.com/api/send.php?number=91{number}&type=text&message={message}&instance_id={instance_id}&access_token={access_token}"
    # url = f"https://x3.woonotif.com/api/send.php?number=91{number}&type=media&message={message}&media_url={file_url}&instance_id={instance_id}&access_token={access_token}"
    
    # # print("\n\n url", url, "\n\n")
    # response = requests.get(url)
    # print("\n\n response", response.text)
    # print("\n\n type response", type(response.text))

    # data = frappe.as_json(response.text)

    data = {'message': {'key': {'remoteJid': '917990915950@c.us', 'fromMe': True, 'id': 'BAE51B3047BA6F4C'}, 'message': {'documentMessage': {'url': 'https://mmg.whatsapp.net/v/t62.7119-24/40116021_1273910713269040_1288344065129231328_n.enc?ccb=11-4&oh=01_AdS2Te3IYQyScs-n1wO7_7v1EVak0e0Mp-Lh9UYPlIeypg&oe=65470DFA&_nc_sid=000000&mms3=true', 'mimetype': 'application/pdf', 'fileSha256': 'FHjwuF3x9HAqsbTACcfze2CgXvbxceiNZOOta/7Z4Kg=', 'fileLength': '24838', 'mediaKey': '6lOdvTjXuwTCLYNKdWm9YMTozmD/HN4x+6rJ9gQqBJo=', 'fileName': 'Payment Entry-ACC-PAY-2023-00002.pdf', 'fileEncSha256': 'yoTZI27Oi5x81EmIVymkAbuqaJlBQcGZmy86bysvy6E=', 'directPath': '/v/t62.7119-24/40116021_1273910713269040_1288344065129231328_n.enc?ccb=11-4&oh=01_AdS2Te3IYQyScs-n1wO7_7v1EVak0e0Mp-Lh9UYPlIeypg&oe=65470DFA&_nc_sid=000000', 'mediaKeyTimestamp': '1696569769', 'caption': 'asdf'}}, 'messageTimestamp': '1696569769'}}

    # data = json.loads(response)


    # Assuming data is a dictionary or JSON object
    if "status" in data and data["status"] == "success":
        # Code to run if "status" is "success"
        print("Status is success.")
    else:
        # Code to run if "status" is not "success" or the key is not present
        print("Status is not success.")

