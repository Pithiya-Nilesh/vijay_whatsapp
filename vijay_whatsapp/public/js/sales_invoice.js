frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
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
                            console.log('Message sent successfully.');
                        } else {
                            // Handle error
                            console.log('Error sending message:', r.exc);
                        }
                    }
                })
            })
        }
	}
})