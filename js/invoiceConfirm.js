$('document').ready(function(){    
    function saveInvoice(){
	$.ajax({
	    url :'/invoiceSave',
	    type: 'GET',
	    data: { "akeys" : akeys.join(":"),
		    "pkey" : $('#pkey').attr('value')},
	    datatype: "json",
	    success: function(json){
		if (alert("Invoice was saved.") === undefined){
		    window.location = "/invoices";
		}
	    },
	    error: function(){
		alert("Invoice was not saved.");
	    }
	});
    }
    $('#save_invoice').click(function(){
	saveInvoice();
    });
    $('#delete_invoice').click(function(){
	ikey= $('#ikey').attr('value');
	window.location="/invoiceDelete?ikey="+ikey;
    });

});