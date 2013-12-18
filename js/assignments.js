$('document').ready(function(){
    function ajaxAssignments(){
	//default dates for start and end are set in html template
	start = $("#start_date").attr('value');
	end = $('#end_date').attr('value');
	project = $('#project').attr('value');
	site = $('#site').attr('value');
	$.ajax({
	    url :'/ajaxAssignment',
	    type: 'GET',
	    data: { "start_date" : start,
		    "end_date" : end,
		    "project" : project,
		    "site" : site} ,
	    dataType: "json",
	    success: function(json){
		console.log(json.join(" : "));
		$('#capacity').html(json[json.length - 1]);
		$status = $('#status');
		$status.html("");
		rows = json.slice(0, json.length - 1);
		for (r in rows){
		    $tr = $('<tr>');
		    $vname = $("<td>");
		    $vname.html(rows[r].vname);
		    $start = $("<td>");
		    $start.html(rows[r].start_date);
		    $end = $("<td>");
		    $end.html(rows[r].end_date);
		    $duration = $("<td>");
		    $duration.html(rows[r].duration);
		    $tr.append($vname);
		    $tr.append($start);
		    $tr.append($end);
		    $tr.append($duration);
		    $status.append($tr);
		}
	    }
	    
	});
    }

    $('#assignment_start_date, #assignment_end_date, #a_project, #a_site').change(function(){
	ajaxAssignments();
    });

    $('#project').change(function(){
	// Removes all options from site selector
	// Appends options for sites for selected project
	var project = $(this);
	var key = $(project).attr('value')
	$('#site').empty();
	siteKeys = siteData[key] // this is set in html template
	for(k in siteKeys){
	    $('#site').append($("<option value='" + siteKeys[k][0] + "'>"+ siteKeys[k][1]+"</option>"));
	    }

	$($('#site')[0]).select();
	ajaxAssignments();
    });

    $('#volunteer').change(function(){
	var key = $(this).attr('value');

	$('input[name=partnerkey]').attr('value', volunteerData[key])
    });

    $('.assignment').each(function(){
	$(this).click(function(){
	    key = $(this).attr('id');
	    if($(this).hasClass('highlighted')){
		$('tr').removeClass('highlighted');
	    } else {
		$('tr').removeClass('highlighted');
		$('tr#'+key).addClass('highlighted');
	    }
	});
    });

 // comment from calendar
    $('.assignmentComment').each(function(){
	$(this).change(function(){
	    id = $(this).attr('id').split(":")[1];
	    comment = $(this).attr('value');

	    $.ajax({
		url :'/ajaxComment',
		type: 'GET',
		data: { "assignmentid" : id,
			"comment" : comment
		      },
		dataType: "json",
		success: function(json){
//		    alert(json.message);
		}
	    });
	    	});
    });
// modify the endDate by selecting # of weeks from dropdown or by changing the start_date.
    $('#nweeks, #start_date').change(function(){
	startDate=$('#start_date').attr('value');
	if (startDate.length != 0){
	    startDate=startDate.split("-");
	    weeks = parseInt($('#nweeks').attr('value'));
	    startDate = new Date(startDate);
	    advance = ((weeks*7) *24*60*60*1000);//- (24*60*60*1000);
	    endDate = new Date(startDate.getTime() + advance);
	    endDateStr = endDate.toISOString().slice(0,10)
	    $('#end_date').attr('value', endDateStr);//endDate.getFullYear()+"-"+(parseInt(endDate.getMonth()) + 1) +"-"+endDate.getDate());
	}
    });
    
    $('.datepicker').datepicker({ dateFormat : "yy-m-d"});

// filter the calendar display
    $('.filter').change(function(){
	console.log($(this).attr('value'));
	params = Array()
	$('.filter').each(function(){
	    if($(this).attr('value') != "-"){
		params.push($(this).attr('name')+"="+$(this).attr('value'));
	    }
	});
	window.location="assignments?"+params.join("&");
    });

})