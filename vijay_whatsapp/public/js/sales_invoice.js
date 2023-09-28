frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
        // frm.doc.set_def_property("custom_whatsapp_no", "read_only", 0);
        if (!frm.is_dirty() || !frm.is_new()){
            frm.add_custom_button(__("Send Whatsapp Message"), function() {
                frappe.call({
                    method: 'vijay_whatsapp.api.on_sales_invoice',
                    args:{
                    'doc': frm.doc.name,
                    'method': 'whitelist'
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            // Handle success
                            frappe.msgprint({
                                title: __('Notification'),
                                indicator: 'green',
                                message: __('Whatsapp Message Sent Successfully')
                            });
                            console.log('Message sent successfully.');
                        } else {
                            // Handle error
                            console.log('Error sending message:', r.exc);
                        }
                    }
                })
            })
        }
	},

    // customer: function (frm){
    //     frm.doc.set_def_property("custom_whatsapp_no", "read_only", 0);
    //     // cur_frm.fields_dict['custom_whatsapp_no'].df.read_only = 0;
    //     cur_frm.refresh_field('custom_whatsapp_no');

    // }
})