$('document').ready(function(){
   // $('.datepicker').datepicker({ dateFormat : "yy-m-d"});
    function ajaxInvoice(){
	//default dates for start and end are set in html template
	start = $("#start_date").attr('value');
	end = $('#end_date').attr('value');
	invoiced = $('#invoiced').attr('checked');
	alldates = $('#alldates').attr('checked');
	partnerkey = $('#partnerkey').attr('value');
	console.info("start ajax.."+"\n"+partnerkey+"\n"+alldates+"\n"+invoiced+"\n"+start+"\n"+end );
	$.ajax({
	    url :'/invoicet',
	    type: 'GET',
	    data: { "partnerkey" : partnerkey,
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
		console.info("response..asdf");
		$('#items').html("")
		console.log(json)
		total = 0
		for(j in json){
		    r = json[j]
		    console.log(json[j]);
		    checked="";
		    invoicedStyle="";
		    if (r.invoiced == true){
			invoicedStyle = "style='background-color:red;'";
			checked="checked";
		    }
		    $('#items').html($("#items").html() + 
				     "<tr><td>"+
				     r.volunteer+"</td><td>"+
				     r.project+"</td><td>"+
				     r.site+"</td><td>"+
				     r.start_date+"</td><td>"+
				     r.end_date+"</td><td>"+
				     r.price.toFixed(2)+"</td><td>"+
				     r.discount.toFixed(2)+"</td><td>"+
				     (r.price-r.discount).toFixed(2)+"</td><td>"+
				     "<input type='checkbox' "+checked+" disabled='disabled'/></td><td>"+
				     "<input type='checkbox' class='akey' name='akey:"+r.key+"'/></td></tr>");
		    total += (r.price - r.discount)
		}
		$('#items').html($("#items").html() +"<tr><td colspan='7'></td><td>"+total.toFixed(2)+"</td></tr>");		}
	});
	console.info("end ajax")
    }
    $('input#start_date.invoice, input#end_date.invoice, input#invoiced.invoice, input#alldates.invoice').change(function(){
	ajaxInvoice();
    });
    //disable the datepickers because when the page loads, alldates is checked
    $('#start_date.invoice, #end_date.invoice').each(function(){
	$(this).datepicker('disable');
	$(this).css('background-color', 'lightgrey');
    });
		   
    //toggle state of datepickers when alldates changes
    $('#alldates').click(function(){
	if ($(this).attr("checked") == "checked"){
	    $('#start_date.invoice, #end_date.invoice').each(function(){
		$(this).datepicker('disable');
		$(this).css('background-color', 'lightgrey');
	    });
	}
	else {
	    $('#start_date.invoice, #end_date.invoice').each(function(){
		$(this).datepicker('enable');
		$(this).css('background-color', 'white');
	    });
	}
    });
    
    function confirmInvoice(){
/*	var akeys = new Array();
	$('.akey').each(function() {
	    akeys.push($(this).attr('name'))
	});
	alert(akeys.join(":"))
*/	$.ajax({
	    url :'/invoiceConfirm',
	    type: 'GET',
	    data: { "akeys" : akeys.join(":"),
		    "pkey" : $('#pkey').attr('value')},
	    datatype: "json",
	    success: function(json){
		$('#accept_invoice').css('background-color', "green");
		$('#accept_invoice').unbind();
	    },
	    error: function(){
		alert("Something went wrong.");
	    }
	});
    }
    $('#accept_invoice').click(function(){
	confirmInvoice();
    });
    $('#delete_invoice').click(function(){
	ikey= $('#ikey').attr('value');
	window.location="/invoiceDelete?ikey="+ikey;
    });
    ajaxInvoice();
})