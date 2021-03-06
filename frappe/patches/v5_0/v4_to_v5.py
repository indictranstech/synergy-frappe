import frappe

def execute():
	changed = (
		("desk", ("feed", "event", "event_role", "todo", "note")),
		("custom", ("custom_field", "custom_script", "customize_form",
			 "customize_form_field", "property_setter")),
		("email", ("bulk_email", "email_alert", "email_alert_recipient", "standard_reply")),
		("geo", ("country", "currency")),
		("print", ("letter_head", "print_format", "print_settings"))
	)
	for module in changed:
		for doctype in module[1]:
			frappe.reload_doc(module[0], "doctype", doctype)
