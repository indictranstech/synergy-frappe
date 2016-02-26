// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

frappe.ui.form.on("Event", "refresh", function(frm,dt,dn) {
  var date = frappe.datetime.now_datetime()
	if(frm.doc.ref_type && frm.doc.ref_name) {
		frm.add_custom_button(__(frm.doc.ref_name), function() {
			frappe.set_route("Form", frm.doc.ref_type, frm.doc.ref_name);
		}, frappe.boot.doctype_icons[frm.doc.ref_type]);
	}
  if(!frm.doc.__islocal ) {
     frm.add_custom_button(__("Create Attendance"), cur_frm.cscript.create_event_attendance,frappe.boot.doctype_icons["Customer"], "btn-default");
  }
  

});

frappe.ui.form.on("Event", "validate", function(frm,doc) {
  var date = frappe.datetime.now_datetime()
   if(frm.doc.starts_on){
    var date = frappe.datetime.now_datetime()
    if(frm.doc.starts_on < date){
      msgprint("Start Date should be todays or greater than todays date.");
      validate= false;
    }
  }
  if(frm.doc.starts_on && frm.doc.ends_on){
    if(frm.doc.starts_on >= frm.doc.ends_on){
      msgprint("End Date should be greater than start date.");
      validate= false;
    }
  }
});

frappe.ui.form.on("Event", "repeat_on", function(frm,doc) {
	if(frm.doc.repeat_on==="Every Day") {
		$.each(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], function(i,v) {
			cur_frm.set_value(v, 1);
		})
	}
});

frappe.ui.form.on("Event", "event_group", function(frm,doc) {
  
  if(frm.doc.event_group==="Only Leaders") {
    set_field_permlevel('roles',0);
    set_field_permlevel('participants',0);

  }
   else {
    set_field_permlevel('roles',3);
    set_field_permlevel('participants',0);
  
  roleshr={
    "Zonal Pastor":"Zonal,Church Group,Church,Only Leaders,PCF,Sr Cell,Cell",
    "Group Church Pastor":"Church Group,Church,Only Leaders,PCF,Sr Cell,Cell",
    "Church Pastor":"Church,Only Leaders,PCF,Sr Cell,Cell",
    "PCF Leader":"Only Leaders,PCF,Sr Cell,Cell",
    "Senior Cell Leader":"Only Leaders,Sr Cell,Cell",
    "Cell Leader":"Cell"
  }

  if(in_list(user_roles, "Zonal Pastor")){
    var desigarray=roleshr['Zonal Pastor'].split(",")
    var inarry=desigarray.indexOf(frm.doc.event_group)
    if (parseInt(inarry) < 0){
      alert ("You have not permitted to select the Event Group "+frm.doc.event_group);
      cur_frm.set_value("event_group","Zonal")                 
      refresh_field("event_group");
      set_field_permlevel('zone',1);
    }  
  }

  else if(in_list(user_roles, "Group Church Pastor")){
    var desigarray=roleshr['Group Church Pastor'].split(",")
    var inarry=desigarray.indexOf(frm.doc.event_group)
    if (parseInt(inarry) < 0){
      alert ("You have not permitted to select the Event Group "+frm.doc.event_group);
      cur_frm.set_value("event_group","Church Group")                 
      refresh_field("event_group");
      set_field_permlevel('church_group',1);
    }  
  }

  else if(in_list(user_roles, "Church Pastor")){
    var desigarray=roleshr['Church Pastor'].split(",")
    var inarry=desigarray.indexOf(frm.doc.event_group)
    if (parseInt(inarry) < 0){
      alert ("You have not permitted to select the Event Group "+frm.doc.event_group);
      cur_frm.set_value("event_group","Church")                 
      refresh_field("event_group");
      set_field_permlevel('church',1);
    }  
  }

  else if(in_list(user_roles, "PCF Leader")){
    var desigarray=roleshr['PCF Leader'].split(",")
    var inarry=desigarray.indexOf(frm.doc.event_group)
    if (parseInt(inarry) < 0){
      alert ("You have not permitted to select the Event Group "+frm.doc.event_group);
      cur_frm.set_value("event_group","PCF")                 
      refresh_field("event_group");
      set_field_permlevel('pcf',1);
    }  
  }

  else if(in_list(user_roles, "Senior Cell Leader")){
    var desigarray=roleshr['Senior Cell Leader'].split(",")
    var inarry=desigarray.indexOf(frm.doc.event_group)
    if (parseInt(inarry) < 0){
      alert ("You have not permitted to select the Event Group "+frm.doc.event_group);
      cur_frm.set_value("event_group","Sr Cell")                 
      refresh_field("event_group");
      set_field_permlevel('senior_cell',1);
      //refresh_field("senior_cell");
    }  
  }

  else if(in_list(user_roles, "Cell Leader")){
    var desigarray=roleshr['Cell Leader'].split(",")
    var inarry=desigarray.indexOf(frm.doc.event_group)
    if (parseInt(inarry) < 0){
      alert ("You have not permitted to select the Event Group "+frm.doc.event_group);
      cur_frm.set_value("event_group","Cell")                 
      refresh_field("event_group");
      set_field_permlevel('cell',1);
    }  
  }
}

});



cur_frm.fields_dict.roles.grid.get_field("role").get_query = function(doc) {
      return {
        query:'church_ministry.church_ministry.doctype.first_timer.first_timer.get_event_roles'
    }
};


frappe.ui.form.on("Event", "onload", function(frm,doc) {
		
		
		if(!frm.doc.__islocal && frm.doc.address) {
      $( "#map-canvas" ).remove();
      $(cur_frm.get_field("address").wrapper).append('<div id="map-canvas" style="width: 425px; height: 425px;"></div>');
			cur_frm.cscript.create_pin_on_map(frm.doc,frm.doc.lat,frm.doc.lon);
			//frm.add_custom_button(__("Create Attendance"), cur_frm.cscript.create_event_attendance,frappe.boot.doctype_icons["Customer"], "btn-default");
		}
    if(frm.doc.event_group==="") {
      set_field_permlevel('participants',3);
    }
});

cur_frm.cscript.create_event_attendance = function() {
		frappe.model.open_mapped_doc({
			method: "church_ministry.church_ministry.doctype.attendance_record.attendance_record.create_event_attendance",
			frm: cur_frm
		})
}

cur_frm.cscript.create_pin_on_map=function(doc,lat,lon){
        var latLng = new google.maps.LatLng(lat, lon);
        var map = new google.maps.Map(document.getElementById('map-canvas'), {
            zoom: 16,
            center: latLng,
            mapTypeId: google.maps.MapTypeId.ROADMAP
          });
        var marker = new google.maps.Marker({
            position: latLng,
            title: 'Point',
            map: map,
            draggable: true
          });

        updateMarkerPosition(latLng);
        geocodePosition(latLng);

        google.maps.event.addListener(marker, 'dragstart', function() {
            updateMarkerAddress('Dragging...');
        });

        google.maps.event.addListener(marker, 'drag', function() {
            updateMarkerStatus('Dragging...');
            updateMarkerPosition(marker.getPosition());
        });

        google.maps.event.addListener(marker, 'dragend', function() {
            updateMarkerStatus('Drag ended');
            geocodePosition(marker.getPosition());
          });
}

function geocodePosition(pos) {
      geocoder.geocode({
        latLng: pos
      }, function(responses) {
        if (responses && responses.length > 0) {
          updateMarkerAddress(responses[0].formatted_address);
        } else {
          if(doc.__islocal) {
            alert('Cannot determine address at this location.');
          }
        }
      });
      geocoder.geocode( { 'address': doc.address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        doc.lat=results[0].geometry.location.lat();
        doc.lon=results[0].geometry.location.lng();
        refresh_field('lat')
        refresh_field('lon')
      } 
    });
}

function updateMarkerAddress(str) {
  doc=cur_frm.doc
  doc.address= str;
  refresh_field('address');
}

function updateMarkerStatus(str) {
var s=1;
}

function updateMarkerPosition(latLng) {
  doc=cur_frm.doc
  doc.lat=latLng.lat()
  doc.lon=latLng.lng()
  refresh_field('lat')
  refresh_field('lon')
}

var geocoder = new google.maps.Geocoder();
var getMarkerUniqueId= function(lat, lng) {
    return lat + '_' + lng;
}

var getLatLng = function(lat, lng) {
    return new google.maps.LatLng(lat, lng);
};

cur_frm.cscript.address = function(doc, dt, dn){
      geocoder.geocode( { 'address': doc.address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
          doc.address=results[0].formatted_address;
          refresh_field('address');
          var latLng = new google.maps.LatLng(results[0].geometry.location.lat(), results[0].geometry.location.lng());
          $( "#map-canvas" ).remove();
          if (doc.address){
            $(cur_frm.get_field("address").wrapper).append('<div id="map-canvas" style="width: 425px; height: 425px;"></div>');
          }
          var map = new google.maps.Map(document.getElementById('map-canvas'), {
              zoom: 16,
              center: latLng,
              mapTypeId: google.maps.MapTypeId.ROADMAP
            });

          var marker = new google.maps.Marker({
              position: latLng,
              title: 'Point',
              map: map,
              draggable: true
            });
          updateMarkerPosition(latLng);
          geocodePosition(latLng);

          google.maps.event.addListener(marker, 'dragend', function() {
              geocodePosition(marker.getPosition());
          });
      } else {
        alert("Geocode was not successful for the following reason: " + status);
      }
    });
}

