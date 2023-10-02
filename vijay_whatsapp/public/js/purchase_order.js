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

    setup(frm){
         // Fetch mobile numbers of users with the role "Accounts Manager"
         frappe.call({
            method: 'vijay_whatsapp.api.get_mobile_numbers',
            args: {
                roles: ['Purchase Manager', 'Purchase Master Manager']
            },
            callback: function(r) {
                if (r.message) {
                    var child_table = frm.doc.custom_whatsapp_no; // Replace with your actual child table fieldname
                    // Clear existing rows in the child table
                    frappe.model.clear_table(cur_frm.doc, "Whatsapp No", "custom_whatsapp_no");

                    // if(child_table === undefined || child_table === '')	       
                    // {
                        for(var data = 0;data < r.message.length; data++){                        
                            var row = frappe.model.add_child(cur_frm.doc, "Whatsapp No", "custom_whatsapp_no");
                            row.whatsapp_no = r.message[data].mobile_no;
                            row.user_name = r.message[data].first_name;
                            row.enable = 1;
                            frm.refresh_fields(child_table);
                        }
                    // }

                }
            }
        });
    }
})