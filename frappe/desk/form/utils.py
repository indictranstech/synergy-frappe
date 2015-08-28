# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe, json
import frappe.desk.form.meta
import frappe.desk.form.load

from frappe import _

@frappe.whitelist()
def remove_attach():
	"""remove attachment"""
	import frappe.utils.file_manager
	fid = frappe.form_dict.get('fid')
	return frappe.utils.file_manager.remove_file(fid)

@frappe.whitelist()
def get_fields():
	"""get fields"""
	r = {}
	args = {
		'select':frappe.form_dict.get('select')
		,'from':frappe.form_dict.get('from')
		,'where':frappe.form_dict.get('where')
	}
	ret = frappe.db.sql("select %(select)s from `%(from)s` where %(where)s limit 1" % args)
	if ret:
		fl, i = frappe.form_dict.get('fields').split(','), 0
		for f in fl:
			r[f], i = ret[0][i], i+1
	frappe.response['message']=r

@frappe.whitelist()
def validate_link():
	"""validate link when updated by user"""
	import frappe
	import frappe.utils

	value, options, fetch = frappe.form_dict.get('value'), frappe.form_dict.get('options'), frappe.form_dict.get('fetch')

	# no options, don't validate
	if not options or options=='null' or options=='undefined':
		frappe.response['message'] = 'Ok'
		return

	if frappe.db.sql("select name from `tab%s` where name=%s" % (options, '%s'), (value,)):

		# get fetch values
		if fetch:
			# escape with "`"
			fetch = ", ".join(("`{0}`".format(f.strip()) for f in fetch.split(",")))

			frappe.response['fetch_values'] = [frappe.utils.parse_val(c) \
				for c in frappe.db.sql("select %s from `tab%s` where name=%s" \
					% (fetch, options, '%s'), (value,))[0]]

		frappe.response['message'] = 'Ok'

@frappe.whitelist()
def add_comment(doc):
	"""allow any logged user to post a comment"""
	record=json.loads(doc)
	if record['comment_doctype']=='Attendance Record':
		mail_notify_msg = """Dear User, <br><br>
									'{0}' had commented '{1}' on the Attendance Record '{2}'. <br><br>Please Check. <br><br>
							Records, <br><br>
							Love World Synergy""".format(record['comment_by'],record['comment'],record['comment_docname'])
		notify = frappe.db.sql("""select value from `tabSingles` where doctype='Notification Settings' and field = 'when_a_leader_makes_a_comment'""",as_list=1)
		hirerchy=frappe.db.sql("select a.name,a.device_id from `tabDefaultValue` b, `tabUser` a where a.name=b.parent and b.defkey='Senior Cells' and b.defvalue=(select senior_cell from `tabAttendance Record` where name='%s')" %record['comment_docname'],as_list=1)
		user = frappe.db.sql("""select phone_1 from `tabMember` where email_id='%s'"""%(hirerchy[0][0]),as_list=1)
		if "Email" in notify[0][0]:
			frappe.sendmail(recipients=hirerchy[0][0], content=mail_notify_msg, subject='Attendance Record comment Notification')
			frappe.sendmail(recipients='gangadhar.k@indictranstech.com', content=mail_notify_msg, subject='Attendance Record comment Notification')
		if "SMS" in notify[0][0]:
			from erpnext.setup.doctype.sms_settings.sms_settings import send_sms			
			if user:
				send_sms(user[0][0], mail_notify_msg)
		if "Push Notification" in notify[0][0]:
			data={}
			data['Message']=mail_notify_msg
			from gcm import GCM
			gcm = GCM('AIzaSyBIc4LYCnUU9wFV_pBoFHHzLoGm_xHl-5k')
			res = gcm.json_request(registration_ids=[x[1] for x in hirerchy], data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)	
	doc = frappe.get_doc(record)
	doc.insert(ignore_permissions = True)

	return doc.as_dict()

@frappe.whitelist()
def get_next(doctype, value, prev, filters=None, order_by="modified desc"):
	import frappe.desk.reportview

	prev = not int(prev)
	sort_field, sort_order = order_by.split(" ")

	if not filters: filters = []
	if isinstance(filters, basestring):
		filters = json.loads(filters)

	# condition based on sort order
	condition = ">" if sort_order.lower()=="desc" else "<"

	# switch the condition
	if prev:
		condition = "<" if condition==">" else "<"
	else:
		sort_order = "asc" if sort_order.lower()=="desc" else "desc"

	# add condition for next or prev item
	if not order_by[0] in [f[1] for f in filters]:
		filters.append([doctype, sort_field, condition, value])

	res = frappe.desk.reportview.execute(doctype,
		fields = ["name"],
		filters = filters,
		order_by = sort_field + " " + sort_order,
		limit_start=0, limit_page_length=1, as_list=True)

	if not res:
		frappe.msgprint(_("No further records"))
		return None
	else:
		return res[0][0]

@frappe.whitelist()
def get_linked_docs(doctype, name, metadata_loaded=None, no_metadata=False):
	if not metadata_loaded: metadata_loaded = []
	meta = frappe.desk.form.meta.get_meta(doctype)
	linkinfo = meta.get("__linked_with")
	results = {}

	if not linkinfo:
		return results

	me = frappe.db.get_value(doctype, name, ["parenttype", "parent"], as_dict=True)
	for dt, link in linkinfo.items():
		link["doctype"] = dt
		link_meta_bundle = frappe.desk.form.load.get_meta_bundle(dt)
		linkmeta = link_meta_bundle[0]
		if not linkmeta.get("issingle"):
			fields = [d.fieldname for d in linkmeta.get("fields", {"in_list_view":1,
				"fieldtype": ["not in", ["Image", "HTML", "Button", "Table"]]})] \
				+ ["name", "modified", "docstatus"]

			fields = ["`tab{dt}`.`{fn}`".format(dt=dt, fn=sf.strip()) for sf in fields if sf]

			try:
				if link.get("get_parent"):
					if me and me.parent and me.parenttype == dt:
						ret = frappe.get_list(doctype=dt, fields=fields,
							filters=[[dt, "name", '=', me.parent]])
					else:
						ret = None

				elif link.get("child_doctype"):
					ret = frappe.get_list(doctype=dt, fields=fields,
						filters=[[link.get('child_doctype'), link.get("fieldname"), '=', name]])

				else:
					ret = frappe.get_list(doctype=dt, fields=fields,
						filters=[[dt, link.get("fieldname"), '=', name]])

			except frappe.PermissionError:
				continue

			if ret:
				results[dt] = ret

			if not no_metadata and not dt in metadata_loaded:
				frappe.local.response.docs.extend(link_meta_bundle)

	return results
