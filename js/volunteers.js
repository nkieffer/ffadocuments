function getVolunteers(){
    var volunteerCount = parseInt(localStorage.getItem("volunteerCount"));
    var volunteers = [];
    for(var i = 0; i <= volunteerCount; i++){
	volunteers.push(localStorage.getItem("volunteer"+parseInt(i)));
    }
    return volunteers;
}

function addVolunteerToList(volunteer){
    $("#results").append($("<tr><td><a href='/volunteerForm?key="+volunteer[5]+"'>"+volunteer[0]+", "+volunteer[1]+"</a></td><td>"+volunteer[2]+"</td><td>"+volunteer[4]+"<td></tr>"));
}

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
		addVolunteerToList(volunteer);
	    }
	    localStorage.setItem("volunteerCount", v);
	}
    });


    $("#query").keyup(function(event){
	$("#results").empty();
	var volunteers = getVolunteers();
	var query = event.target.value;
	console.log(query);
	if (query == ""){
	    volunteers.map(function(v){addVolunteerToList(v.split(","));});
	} else {
	    for( var v in volunteers ){
		var volunteer = volunteers[v].split(",").slice(0,5);
		console.log(volunteer[0])
		console.log(volunteer[0].search(query));
		matches = volunteer.map(function(prop){ 
		    if (prop.search(query) > -1){
			return true;
		    } else {
			return false; 
		    }
		});
		
		if (matches.indexOf(true) > -1){
		    addVolunteerToList(volunteer);
		}
	    }
	    
	}
    });	    
});