$(document).ready(function(){
    var Router = Backbone.Router.extend({
	routes: {
	    "home" : "home",
	    "partners": "partnerList",
	    "projects": "projectList",
	    "volunteers": "volunteerList",
	    "assignments": "assignmentList",
	    "invoices": "invoiceList"
	},
	templates: {
	    partners: _.template($("#partnerListTemplate").html())
	},
	home: function(){
	    console.log("Request for /#home");
	},
	partnerList: function(){
	    console.log("Request for /#partners");
	    var partners = [{"name": "Beans", "_id": "asdf34"},
			    {"name": "Beans", "_id": "asdf34"},
			    {"name": "Beans", "_id": "asdf34"}]
	    $('#main').html(this.templates.partners({ "partners": partners}));
	},
	projectList: function(){
	    console.log("Request for /#projects");
	},
	volunteerList: function(){
	    console.log("Request for /#volunteers");
	},
	invoiceList: function(){
	    console.log("Request for /#invoices");
	}
    });
    var router = new Router();
    Backbone.history.start()

});