$(document).ready(function(){
    document.PartnerModel = Backbone.Model.extend({
	defaults: {
/*	    name = db.StringProperty()
	    abbr = db.StringProperty()
	    comment = db.TextProperty()
	    address = db.TextProperty()
*/
	    name: "",
	    abbr: "",
	    comment: "",
	    address: "",
	    id: null
	},
	changeAction: function() { 
		document.actionCollection.add({
			action: "Modified partner: "+this.get("name"), 
			result: "success",
			 timestamp: new Date()},
			 this);
	},
	destroyAction: function () { 
		document.actionCollection.add({
			action: "Deleted partner: "+this.get("name"), 
			result: "success",
			 timestamp: new Date()},
			 this);
	},

                            
                     
	//idAttribute: "key"
    });

    document.PartnerCollection = Backbone.Collection.extend({
	url: "partners",
	model: document.PartnerModel,
	renderTable: function(){
		//var this = document.partnerCollection;
		if ( this.updated === true) {
			this.forEach( function(partner, idx, list) {
				console.dir(partner);
            	var pv = new document.PartnerListView(partner);
            	pv.render();
        	});
		}else{
		//	partners = this
			this.fetch({
                success: function(partners, response, opts) {
                    partners.updated = true;
                    partners.forEach( function(partner, idx, list) {
                        var pv = new document.PartnerListView(partner);
                        pv.render();
                    });
                },
                error: function(partners, response, opts) {
                    console.log("Error loading partners from server.")
                }  
            });
		}
	}	

    });

    document.partnerCollection = new document.PartnerCollection();
    document.partnerCollection.on({
    	"add": function(partner) { 
    			var action = new document.ActionModel({
    			action: "Added new partner: " + partner.get("name"),
    			result: "success",
    		});
    	}
    });
    document.PartnerListView = Backbone.View.extend({
	el: '#partnerTable tbody',
	tpl: _.template($('#partnerTableRowTemp').html()),
	render: function(){
	    this.$el.append(this.tpl(this.attributes));
	    return this;
	}
    });

});