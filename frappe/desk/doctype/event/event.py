# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import getdate, cint, add_months, date_diff, add_days, nowdate
from frappe.model.document import Document
from frappe.utils.user import get_enabled_system_users

weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

class Event(Document):
	def validate(self):
		if self.starts_on and self.ends_on and self.starts_on > self.ends_on:
			frappe.msgprint(frappe._("Event end must be after start"), raise_exception=True)

		if self.starts_on == self.ends_on:
			# this scenario doesn't make sense i.e. it starts and ends at the same second!
			self.ends_on = None

		if self.starts_on and self.ends_on and int(date_diff(self.ends_on.split(" ")[0], self.starts_on.split(" ")[0])) > 0 \
			and self.repeat_on == "Every Day":
			frappe.msgprint(frappe._("Every day events should finish on the same day."), raise_exception=True)

	# def set_higher_values(self):
	# 	if self.region:
	# 		value = frappe.db.sql("select zone,church_group,church,pcf,senior_cell,name from `tabCell Master` where region='%s'"%(self.region),as_list=1)
	# 		ret={}
	# 		if value:
	# 			ret={
	# 				"zone": value[0][0],
	# 				"church_group": value[0][1],
	# 				"church" : value[0][2],
	# 				"pcf" : value[0][3],
	# 				"senior_cell" : value[0][4],
	# 				"cell" : value[0][5]
	# 			}
	# 		return ret
	# 	elif self.zone:
	# 		value = frappe.db.sql("select region,church_group,church,pcf,senior_cell,name from `tabCell Master` where zone='%s'"%(self.zone),as_list=1)
	# 		ret={}
	# 		if value:
	# 			ret={
	# 				"region": value[0][0],
	# 				"church_group": value[0][1],
	# 				"church" : value[0][2],
	# 				"pcf" : value[0][3],
	# 				"senior_cell" : value[0][4],
	# 				"cell" : value[0][5]
	# 			}
	# 		return ret
	# 	elif self.church_group:
	# 		value = frappe.db.sql("select region,zone,church,pcf,senior_cell,name from `tabCell Master` where church_group='%s'"%(self.church_group),as_list=1)
	# 		ret={}
	# 		if value:
	# 			ret={
	# 				"region": value[0][0],
	# 				"zone": value[0][1],
	# 				"church" : value[0][2],
	# 				"pcf" : value[0][3],
	# 				"senior_cell" : value[0][4],
	# 				"cell" : value[0][5]
	# 			}
	# 		return ret
	# 	elif self.church:
	# 		value = frappe.db.sql("select region,zone,church_group,pcf,senior_cell,name from `tabCell Master` where church='%s'"%(self.church),as_list=1)
	# 		ret={}
	# 		if value:
	# 			ret={
	# 				"region": value[0][0],
	# 				"zone": value[0][1],
	# 				"church_group" : value[0][2],
	# 				"pcf" : value[0][3],
	# 				"senior_cell" : value[0][4],
	# 				"cell" : value[0][5]
	# 			}
	# 		return ret
	# 	elif self.pcf:
	# 		value = frappe.db.sql("select region,zone,church_group,church,senior_cell,name from `tabCell Master` where pcf='%s'"%(self.pcf),as_list=1)
	# 		ret={}
	# 		if value:
	# 			ret={
	# 				"region": value[0][0],
	# 				"zone": value[0][1],
	# 				"church_group" : value[0][2],
	# 				"church" : value[0][3],
	# 				"senior_cell" : value[0][4],
	# 				"cell" : value[0][5]
	# 			}
	# 		return ret
	# 	elif self.senior_cell:
	# 		value = frappe.db.sql("select region,zone,church_group,church,pcf,name from `tabCell Master` where senior_cell='%s'"%(self.senior_cell),as_list=1)
	# 		ret={}
	# 		if value:
	# 			ret={
	# 				"region": value[0][0],
	# 				"zone": value[0][1],
	# 				"church_group" : value[0][2],
	# 				"church" : value[0][3],
	# 				"pcf" : value[0][4],
	# 				"cell" : value[0][5]
	# 			}
	# 		return ret
	# 	elif self.cell:
	# 		value = frappe.db.sql("select region,zone,church_group,church,pcf,senior_cell from `tabCell Master` where name='%s'"%(self.cell),as_list=1)
	# 		ret={}
	# 		if value:
	# 			ret={
	# 				"region": value[0][0],
	# 				"zone": value[0][1],
	# 				"church_group" : value[0][2],
	# 				"church" : value[0][3],
	# 				"pcf" : value[0][4],
	# 				"senior_cell" : value[0][5]
	# 			}
	# 		return ret

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	abc="""(tabEvent.event_type='Public' or tabEvent.owner='%(user)s'
		or exists(select * from `tabEvent Role` where
			`tabEvent Role`.parent=tabEvent.name
			and `tabEvent Role`.role in ('%(roles)s')))
		or 
		tabEvent.cell=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Cell Master')
		or
		tabEvent.senior_cell=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Senior Cell Master')
		or
		tabEvent.pcf=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='PCF Master')
		or
		tabEvent.church=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Church Master')
		or
		tabEvent.church_group=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Group Church Master')
		or
		tabEvent.zone=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Zone Master')
		or
		tabEvent.region=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Region Master')
		""" % {
			"user": frappe.db.escape(user),
			"roles": "', '".join([frappe.db.escape(r) for r in frappe.get_roles(user)])
		}
	# frappe.errprint(abc)
	return abc

def has_permission(doc, user):
	if doc.event_type=="Public" or doc.owner==user:
		frappe.errprint("first if")
		return True

	if doc.get("roles", {"role":("in", frappe.get_roles(user))}):
		frappe.errprint("second if")
		return True

	if doc.cell:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Cell Master'"%(user),debug=1)
		frappe.errprint(res)
		if res:
			return True

	if doc.senior_cell:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Senior Cell Master'"%(user),debug=1)
		frappe.errprint(res)
		if res:
			return True

	if doc.pcf:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='PCF Master'"%(user),debug=1)
		frappe.errprint(res)
		if res:
			return True

	if doc.church:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Church Master'"%(user),debug=1)
		frappe.errprint(res)
		if res:
			return True

	if doc.church_group:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Church Master'"%(user),debug=1)
		frappe.errprint(res)
		if res:
			return True

	if doc.zone:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Church Master'"%(user),debug=1)
		frappe.errprint(res)
		if res:
			return True

	if doc.region:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Church Master'"%(user),debug=1)
		frappe.errprint(res)
		if res:
			return True

	return False


def send_event_digest():
	today = nowdate()
	for user in get_enabled_system_users():
		events = get_events(today, today, user.name, for_reminder=True)
		if events:
			text = ""
			frappe.set_user_lang(user.name, user.language)

			text = "<h3>" + frappe._("Events In Today's Calendar") + "</h3>"
			for e in events:
				if e.all_day:
					e.starts_on = "All Day"
				text += "<h4>%(starts_on)s: %(subject)s</h4><p>%(description)s</p>" % e

			text += '<p style="color: #888; font-size: 80%; margin-top: 20px; padding-top: 10px; border-top: 1px solid #eee;">'\
				+ frappe._("Daily Event Digest is sent for Calendar Events where reminders are set.")+'</p>'

			frappe.sendmail(recipients=user.email, subject=frappe._("Upcoming Events for Today"),
				content = text, bulk=True)

@frappe.whitelist()
def get_events(start, end, user=None, for_reminder=False):
	if not user:
		user = frappe.session.user
	roles = frappe.get_roles(user)
	events = frappe.db.sql("""select name, subject, description,
		starts_on, ends_on, owner, all_day, event_type, repeat_this_event, repeat_on,repeat_till,
		monday, tuesday, wednesday, thursday, friday, saturday, sunday
		from tabEvent where ((
			(date(starts_on) between date('%(start)s') and date('%(end)s'))
			or (date(ends_on) between date('%(start)s') and date('%(end)s'))
			or (date(starts_on) <= date('%(start)s') and date(ends_on) >= date('%(end)s'))
		) or (
			date(starts_on) <= date('%(start)s') and ifnull(repeat_this_event,0)=1 and
			ifnull(repeat_till, "3000-01-01") > date('%(start)s')
		))
		%(reminder_condition)s
		and (event_type='Public' or owner='%(user)s'
		or exists(select name from `tabDocShare` where
			tabDocShare.share_doctype="Event" and `tabDocShare`.share_name=tabEvent.name
			and tabDocShare.user='%(user)s')
		or exists(select * from `tabEvent Role` where
			`tabEvent Role`.parent=tabEvent.name
			and `tabEvent Role`.role in ('%(roles)s')))
		order by starts_on""" % {
			"start": start,
			"end": end,
			"reminder_condition": "and ifnull(send_reminder,0)=1" if for_reminder else "",
			"user": user,
			"roles": "', '".join(roles)
		}, as_dict=1)

	# process recurring events
	start = start.split(" ")[0]
	end = end.split(" ")[0]
	add_events = []
	remove_events = []

	def add_event(e, date):
		new_event = e.copy()

		enddate = add_days(date,int(date_diff(e.ends_on.split(" ")[0], e.starts_on.split(" ")[0]))) \
			if (e.starts_on and e.ends_on) else date
		new_event.starts_on = date + " " + e.starts_on.split(" ")[1]
		if e.ends_on:
			new_event.ends_on = enddate + " " + e.ends_on.split(" ")[1]
		add_events.append(new_event)

	for e in events:
		if e.repeat_this_event:
			event_start, time_str = e.starts_on.split(" ")
			if e.repeat_till == None or "":
				repeat = "3000-01-01"
			else:
				repeat = e.repeat_till
			if e.repeat_on=="Every Year":
				start_year = cint(start.split("-")[0])
				end_year = cint(end.split("-")[0])
				event_start = "-".join(event_start.split("-")[1:])

				# repeat for all years in period
				for year in range(start_year, end_year+1):
					date = str(year) + "-" + event_start
					if date >= start and date <= end and date <= repeat:
						add_event(e, date)

				remove_events.append(e)

			if e.repeat_on=="Every Month":
				date = start.split("-")[0] + "-" + start.split("-")[1] + "-" + event_start.split("-")[2]

				# last day of month issue, start from prev month!
				try:
					getdate(date)
				except ValueError:
					date = date.split("-")
					date = date[0] + "-" + str(cint(date[1]) - 1) + "-" + date[2]

				start_from = date
				for i in xrange(int(date_diff(end, start) / 30) + 3):
					if date >= start and date <= end and date <= repeat and date >= event_start:
						add_event(e, date)
					date = add_months(start_from, i+1)

				remove_events.append(e)

			if e.repeat_on=="Every Week":
				weekday = getdate(event_start).weekday()
				# monday is 0
				start_weekday = getdate(start).weekday()

				# start from nearest weeday after last monday
				date = add_days(start, weekday - start_weekday)

				for cnt in xrange(int(date_diff(end, start) / 7) + 3):
					if date >= start and date <= end and date <= repeat and date >= event_start:
						add_event(e, date)

					date = add_days(date, 7)

				remove_events.append(e)

			if e.repeat_on=="Every Day":
				for cnt in xrange(date_diff(end, start) + 1):
					date = add_days(start, cnt)
					if date >= event_start and date <= end and date <= repeat \
						and e[weekdays[getdate(date).weekday()]]:
						add_event(e, date)
				remove_events.append(e)

	for e in remove_events:
		events.remove(e)

	events = events + add_events

	for e in events:
		# remove weekday properties (to reduce message size)
		for w in weekdays:
			del e[w]

	return events
