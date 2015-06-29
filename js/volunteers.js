$(document).ready(function(){
    if (typeof(Storage) !== 'undefined'){
	v = "";
    }else{
	v = "un";
    }
    console.log("Storage " + v +"available.");
    $.ajax({
	url :'/volunteerRetrieveCache',
	type: 'GET',
	data: {},
	dataType: "json",
	success: function(json){
	    for ( var v in json ){
		var volunteer = json[v];
		localStorage.setItem("volunteer"+v, volunteer);
	    }
	    localStorage.setItem("volunteerCount", v);
	}
    });
    function getVolunteers(){
	var volunteerCount = parseInt(localStorage.getItem("volunteerCount"));
	var volunteers = [];
	for(var i = 0; i <= volunteerCount; i++){
	    volunteers.push(localStorage.getItem("volunteer"+i));
	}
	return volunteers;
    }

    $("#query").keyup(function(event){
	$("#results").empty();
	var volunteers = getVolunteers();
	var query = event.target.value;
	console.log(query);
	for( var v in volunteers ){
	    var volunteer = volunteers[v].split(",");
	    if (volunteer.slice(0,5).map(function(v){ return true ? v.search(query) >= 0 : false; }).indexOf(true) > 0){
		$("#results").append($("<li>"+volunteer+"</li>"));
	    
	    }
	}
    }
    );	    
});