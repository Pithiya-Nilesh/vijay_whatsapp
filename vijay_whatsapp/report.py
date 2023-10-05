import frappe
from frappe.utils.data import get_url
from frappe.email.doctype.auto_email_report.auto_email_report import make_links, update_field_types

@frappe.whitelist(allow_guest=True)
# def get_report_content(report="", report_type='', filters={'company': 'Vijay Mamra Private Limited', 'ageing_based_on': 'Due Date', 'range1': '30', 'range2': '60', 'range3': '90', 'range4': '120'}, data_modified_till=""):
def get_report_content(name):
    filters = {'company': 'Vijay Mamra Private Limited', 'ageing_based_on': 'Due Date', 'range1': '30', 'range2': '60', 'range3': '90', 'range4': '120', 'party_type': 'Customer', 'party': name}
    """Returns file in for the report in given format"""
    
    report = frappe.get_doc("Report", "Accounts Receivable")

    filters = frappe.parse_json(filters) if filters else {}

    columns, data = report.get_data(
        limit= 100,
        user= frappe.session.user,
        filters= filters,
        as_dict=True,
        ignore_prepared_report=True,
        are_default_filters=False,
    )
   
    # add serial numbers
    columns.insert(0, frappe._dict(fieldname="idx", label="", width="30px"))
    for i in range(len(data)):
        data[i]["idx"] = i + 1

    # if format == "HTML":
    columns, data = make_links(columns, data)
    # print("\n\n data", data)

    columns = update_field_types(columns)

    return get_html_table(columns, data)


def get_html_table(columns=None, data=None):
    from datetime import timedelta
    from frappe.utils import (
	add_to_date,
	cint,
	format_time,
	get_link_to_form,
	get_url_to_report,
	global_date_format,
	now,
	now_datetime,
	today,
	validate_email_address,
)

    # print("\n\n column", columns)
    # print("\n\n data", data)
    date_time = global_date_format(now()) + " " + format_time(now())
    report_doctype = frappe.db.get_value("Report", "Accounts Receivable", "ref_doctype")

    return frappe.render_template(
        # "frappe/templates/emails/auto_email_report.html",
        "vijay_whatsapp/templates/whatsapp_report.html",
        {
            "title": "Accounts Receivable",
            "description": "this is description",
            "date_time": date_time,
            "columns": columns,
            "data": data,
            "report_url": get_url_to_report("Accounts Receivable", "Script Report", report_doctype),
            "report_name": "Auto Email Report",
            "edit_report_settings": get_link_to_form("Auto Email Report", "Accounts Receivable"),
        },
    )





# def get_url_to_report(name, report_type: str | None = None, doctype: str | None = None) -> str:
#     from frappe.desk.utils import slug
#     if report_type == "Report Builder":
#         return get_url(uri=f"/app/{quoted(slug(doctype))}/view/report/{quoted(name)}")
#     else:
#         return get_url(uri=f"/app/query-report/{quoted(name)}")


# def get_link_to_form(doctype: str, name: str, label: str | None = None) -> str:
# 	if not label:
# 		label = name

# 	return f"""<a href="{get_url_to_form(doctype, name)}">{label}</a>"""


# def get_url_to_form(doctype: str, name: str) -> str:
#     from frappe.desk.utils import slug
#     return get_url(uri=f"/app/{quoted(slug(doctype))}/{quoted(name)}")


# def quoted(url: str) -> str:
#     from urllib.parse import quote, urljoin
#     return cstr(quote(encode(cstr(url)), safe=b"~@#$&()*!+=:;,.?/'"))

# def cstr(s, encoding="utf-8"):
# 	return frappe.as_unicode(s, encoding)

# def encode(obj, encoding="utf-8"):
# 	if isinstance(obj, list):
# 		out = []
# 		for o in obj:
# 			if isinstance(o, str):
# 				out.append(o.encode(encoding))
# 			else:
# 				out.append(o)
# 		return out
# 	elif isinstance(obj, str):
# 		return obj.encode(encoding)
# 	else:
# 		return obj
    

# def make_links(columns, data):
#     for row in data:
#         doc_name = row.get("name")
#         for col in columns:
#             if not row.get(col.fieldname):
#                 continue

#             if col.fieldtype == "Link":
#                 if col.options and col.options != "Currency":
#                     row[col.fieldname] = get_link_to_form(col.options, row[col.fieldname])
#             elif col.fieldtype == "Dynamic Link":
#                 if col.options and row.get(col.options):
#                     row[col.fieldname] = get_link_to_form(row[col.options], row[col.fieldname])
#             elif col.fieldtype == "Currency":
#                 doc = frappe.get_doc(col.parent, doc_name) if doc_name and col.get("parent") else None
#                 # Pass the Document to get the currency based on docfield option
#                 row[col.fieldname] = frappe.format_value(row[col.fieldname], col, doc=doc)
#     return columns, data


# def update_field_types(columns):
# 	for col in columns:
# 		if col.fieldtype in ("Link", "Dynamic Link", "Currency") and col.options != "Currency":
# 			col.fieldtype = "Data"
# 			col.options = ""
# 	return columns
