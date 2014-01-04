$('document').ready(function(){
   // $('.datepicker').datepicker({ dateFormat : "yy-m-d"});
    function ajaxInvoice(){
	//default dates for start and end are set in html template
	start = $("#start_date").attr('value');
	end = $('#end_date').attr('value');
	invoiced = $('#invoiced').attr('checked');
	alldates = $('#alldates').attr('checked');
	partnerkey = $('#partnerkey').attr('value');
	invoicekey = $('#invoicekey').attr('value');
	$.ajax({
	    url :'/invoiceJSON',
	    type: 'GET',
	    data: {
		"invoicekey" : invoicekey,
		"partnerkey" : partnerkey,
		    "start_date" : start,
		    "end_date" : end,
		    'invoiced' : invoiced,
		    'alldates' : alldates },
	    dataType: "json",
	    beforeSend: function(){
		$('#items').html("Loading...");
	    },
	    error: function(){
		$('#items').html("Sumfin effed up");
	    },
	    success: function(json){
		$('#items').html("")
		total = 0
		for(j in json.assignments){
		    r = json.assignments[j]
		    checked="";
		    invoicedStyle="";
		    if (r.invoiced == true){
			invoicedStyle = "style='background-color:red;'";
			checked="checked";
		    }
		    on_invoice = ""
		    if (json.on_invoice.indexOf(r.key) >= 0){
			on_invoice="checked"
		    }
		    $('#items').html($("#items").html() + 
				     "<tr><td>"+
				     r.volunteer+"</td><td>"+
				     r.project+"</td><td>"+
				     r.site+"</td><td>"+
				     r.start_date+"</td><td>"+
				     r.end_date+"</td><td>"+
				     r.duration +"</td><td>"+
				     r.price.toFixed(2)+"</td><td>"+
				     r.additionalWeeks + "</td><td>"+
				     r.additionalWeekPrice + "</td><td>"+
				     r.discount.toFixed(2)+"</td><td>"+
				     ((r.price + (r.additionalWeeks * r.additionalWeekPrice))-r.discount).toFixed(2)+"</td><td>"+
				     "<input type='checkbox' "+checked+" disabled='disabled'/></td><td>"+
				     "<input type='checkbox' class='akey' name='akey:"+r.key+"' "+ on_invoice +"/></td></tr>");
		    total += (r.price - r.discount)
		}
		$('#items').html($("#items").html() +"<tr><td colspan='7'></td><td>"+total.toFixed(2)+"</td></tr>");		}
	});
    }
    $('input#start_date.invoice, input#end_date.invoice, input#invoiced.invoice, input#alldates.invoice').change(function(){
	ajaxInvoice();
    });

    $('.datepicker').datepicker({ dateFormat : "yy-m-d"});
    //disable the datepickers because when the page loads, alldates is checked

    $('#start_date, #end_date').each(function(){
	$(this).datepicker('disable');
	$(this).css('background-color', 'lightgrey');
    });
		   
    //toggle state of datepickers when alldates changes
    $('#alldates').change(function(){
	if ($(this).attr("checked") == "checked"){
	    $('#start_date, #end_date').each(function(){
		$(this).datepicker('disable');
		$(this).css('background-color', 'lightgrey');
	    });
	}
	else {
	    $('#start_date, #end_date').each(function(){
		$(this).datepicker('enable');
		$(this).css('background-color', 'white');
	    });
	}
    });
    $('#include_all').change(function(){
	checked = $(this).attr("checked") == "checked"
	$('.akey').each(function(){
	    $(this).attr("checked", checked)
	});
    });
    ajaxInvoice();
})