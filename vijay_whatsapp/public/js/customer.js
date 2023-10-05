frappe.ui.form.on('Customer', {
	refresh(frm) {
        frm.add_custom_button(__("Send Account Receivable"), function() {
            frappe.call({
                method: 'vijay_whatsapp.api.on_customer_receivable',
                args:{
                'doc': frm.doc.name,
                },
                callback: function(r) {
                    if (!r.exc) {
                        // Handle success
                        frappe.msgprint({
                            title: __('Notification'),
                            indicator: 'green',
                            message: __('Whatsapp Message Queue Successfully.')
                        });
                        console.log('Message sent successfully.');
                    } else {
                        // Handle error
                        console.log('Error sending message:', r.exc);
                    }
                }
            })
        }, ("Whatsapp"))
    }
})

// function pdf_report(print_settings) {
//     const base_url = frappe.urllib.get_base_url();
//     const print_css = frappe.boot.print_css;
//     const landscape = "Landscape";

//     const custom_format = this.report_settings.html_format || null;
//     const columns = this.get_columns_for_print(print_settings, custom_format);
//     const data = this.get_data_for_print();
//     const applied_filters = this.get_filter_values();

//     const filters_html = this.get_filters_html_for_print();
//     const template = columns || !custom_format ? "print_grid" : custom_format;
//     const content = frappe.render_template(template, {
//         title: __(this.report_name),
//         subtitle: filters_html,
//         filters: applied_filters,
//         data: data,
//         original_data: this.data,
//         columns: columns,
//         report: this,
//     });

//     // Render Report in HTML
//     const html = frappe.render_template("print_template", {
//         title: __(this.report_name),
//         content: content,
//         base_url: base_url,
//         print_css: print_css,
//         print_settings: print_settings,
//         landscape: landscape,
//         columns: columns,
//         lang: frappe.boot.lang,
//         layout_direction: frappe.utils.is_rtl() ? "rtl" : "ltr",
//         can_use_smaller_font: this.report_doc.is_standard === "Yes" && custom_format ? 0 : 1,
//     });

//     console.log("asdf", html)

//     let filter_values = [],
//         name_len = 0;
//     for (var key of Object.keys(applied_filters)) {
//         name_len = name_len + applied_filters[key].toString().length;
//         if (name_len > 200) break;
//         filter_values.push(applied_filters[key]);
//     }
//     print_settings.report_name = `${__(this.report_name)}_${filter_values.join("_")}.pdf`;
//     frappe.render_pdf(html, print_settings);
// }