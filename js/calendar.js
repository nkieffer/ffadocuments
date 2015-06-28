function getWeeksRemaining(endDate,  currentDate) {
    var one_day = 1000*60*60*24;
    var endDate = endDate.getTime();
    var currentDate = currentDate.getTime();
    var diff = endDate - currentDate;
    var weeks = Math.round(diff/one_day/7);
    return weeks;
}

function offSetDate(date, offset){
    var one_day = 1000*60*60*24;
    var time = date.getTime();
    var offset = time + (one_day * offset);
    return new Date(offset);
}

$(document).ready(function(){
    //Initialize data settings for filter
    $("td").each(function(){
	$(this).data("filtered", "false");
    });

    //Set weeks remaining td for each assignment
    $("td.weeksRemaining").each(function(){
	$(this).html(
	    getWeeksRemaining(
		new Date(
		    $(this).data('endyear'),
		    $(this).data('endmonth'),
		    $(this).data('endday')
		),
		new Date(
		    $(this).data('weekyear'),
		    $(this).data('weekmonth'),
		    $(this).data('weekday')
		)
	    )
	);
    });
 //Hide and Show weekly assignments.   
    $('.weekHead').click(function(){
	var tbody = $(this).next();
	tbody.toggleClass('hidden');
	$('tr.assignmentHeadings', this).toggleClass('hidden');
    });

    $('button#showAll').click(function(){
	$('.weekList').each(function(){
	    $(this).prev().find('.assignmentHeadings').removeClass('hidden');
	    $(this).removeClass('hidden');
	});
    });

    $('button#hideAll').click(function(){
	$('.weekList').each(function(){
	    $(this).prev().find('.assignmentHeadings').addClass('hidden');
	    $(this).addClass('hidden');
	});
    });

    $("button#toggleAll").click(function(){
	$('.weekList').each(function(){
	    $(this).prev().find('.assignmentHeadings').toggleClass('hidden');
	    $(this).toggleClass('hidden');
	});
    });

    

    //Set status code for each assignment
    $("td.code").each(function(){
	var code;
	var start_date = new Date($(this).data('startdate'));
	var end_date = new Date($(this).data('enddate'));
	var week = new Date($(this).data('week'));
	var weektbody = $(this).parent().parent()
	if (week.toString() == start_date.toString()){
	    $(this).html("S");
	    weektbody.data('starts', parseInt(weektbody.data('starts')) + 1);
	}
	if (offSetDate(week, 7).toString() == end_date.toString()){
	    $(this).html("F");
	    weektbody.data('finishes', parseInt(weektbody.data('finishes')) + 1);
	}
    });

    //Create volunteer count summary for each week
    $("tbody.weekList").each(function(){
	var thead = $(this).prev()
	var starts = $(this).data('starts');
	var finishes = $(this).data('finishes');
	$("span.starts", thead).html(starts);
	$("span.finishes", thead).html(finishes);
    });

    //Create project count summary for each week
    $("tbody.weekList").each(function(){
	var counts = {}
	$("tr.assignment", $(this)).each(function(){
	    var project_name = $(this).data('project');
	    var code = $(this).find('.code')[0].innerHTML;
	    if(counts.hasOwnProperty(project_name)){
		counts[project_name].total += 1
		
	    }else{
		counts[project_name] = {total: 1, start: 0, finish: 0};
	    }
	    if(code == "S"){
		counts[project_name].start += 1;
	    }
	    if (code == "F"){
		counts[project_name].finish += 1;
	    }
	});
	var countKeys = Object.keys(counts).sort();
	if(countKeys.length == 0){
	    $($(this).prev().children()[1]).addClass('hidden');
	}else{
	    for(var i in countKeys){
		var project = countKeys[i];
		$("<tr class='projectSummary'><th colspan='4'>"+project+"</th><td>"+counts[project].total+"</td><td>"+counts[project].start+"</td><td>"+counts[project].finish+"</td></tr>").insertAfter($(".weekSummary", $(this).prev()));
	    }
	}
    });

    //Highlighting
    $("tr.assignment").mouseover(function(){
	assignment = $(this).attr('data-assignment');
	$('tr.assignment').each(function(){
	    $(this).removeClass('highlight');
	});
	$("[data-assignment="+assignment+"]").each(function(){
	    $(this).addClass('highlight');
	});
    });

    $('table').mouseout(function(){
	$('tr.assignment').each(function(){
	    $(this).removeClass('highlight');
	});
    });

    //filter by partner
    $(".partner_name").click(function(){
	var partner_name = $(this).attr('data-partner');
	$("td.partner_name[data-partner!='"+partner_name+"']").each(function(){
	    if ($(this).data('filtered') == 'true'){
		$(this).parent().removeClass('hidden');
		$(this).data('filtered', 'false');
	    }else{
		$(this).parent().addClass('hidden');
		$(this).data('filtered', 'true');
	    }
	});
    });

    //filter by project
    $(".project_name").click(function(){
	var project_name = $(this).attr('data-project');
	$("td.project_name[data-project!='"+project_name+"']").each(function(){
	    if ($(this).data('filtered') == 'true'){
		$(this).parent().removeClass('hidden');
		$(this).data('filtered', 'false');
	    }else{
		$(this).parent().addClass('hidden');
		$(this).data('filtered', 'true');
	    }
	});
    });

    //filter by volunteer
    $(".volunteer_name").click(function(){
	var volunteer_name = $(this).attr('data-volunteer');
	$("td.volunteer_name[data-volunteer!='"+volunteer_name+"']").each(function(){
	    if ($(this).data('filtered') == 'true'){
		$(this).parent().removeClass('hidden');
		$(this).data('filtered', 'false');
	    }else{
		$(this).parent().addClass('hidden');
		$(this).data('filtered', 'true');
	    }
	});
    });

    //clear all filters
    $("#clearFilters").click(function(){
	$('tr.assignment').each(function(){
	    $(this).removeClass('hidden');
	});
	$('td').each(function(){
	    $(this).data('filtered', 'false');
	});
    });

    $(".info").click(function(){
	$(this).remove();
    });
});
