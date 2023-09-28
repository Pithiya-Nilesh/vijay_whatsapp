frappe.ui.form.on('Purchase Order', {
	refresh(frm) {
        // frm.doc.set_def_property("custom_whatsapp_no", "read_only", 0);
        if (!frm.is_dirty() || !frm.is_new()){
                frm.add_custom_button(__("Send Whatsapp Message"), function() {
                    frappe.call({
                        method: 'vijay_whatsapp.api.on_purchase_order',
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
                                    message: __('Whatsapp Message Queue Successfully.')
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
})