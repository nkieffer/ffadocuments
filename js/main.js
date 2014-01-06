$('document').ready(function(){
    $('.first').focus();
    //Confirm deletions from anchors.
    $('.delete').click(function(){
	var classes = $(this).attr('class').split(/\s+/);
	var dbmodel = classes[1]

	switch (dbmodel)
	{
	case "volunteer":
	    var warn = "This will also delete all of this volunteers project assignments."
	    break;

	case "project":
	    var warn = "This will also delete all of this projects sites."
	    break;
	default:
	    var warn = "";
	    break;

	}
	return confirm("Are you sure you want to delete this " + dbmodel + "?\n"+
		       warn + "\n" +
		       "It cannot be undone!!\n\n" +
		       "Click OK to delete."
		      );
    });
//	try {

//	}catch (err){
		
//	}
	
  //  }
    //ajaxInvoice();
})