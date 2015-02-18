$(document).ready(function(){
    document.ActionModel = Backbone.Model.extend({
	defaults: {
        action: "",
	    result: "",
	    timestamp: null,
	   }
    });

    document.ActionCollection = Backbone.Collection.extend({
	   url: "actions",
	   model: document.ActionModel
    });

    document.actionCollection = new document.ActionCollection();
    document.actionCollection.on("add", function(action, collection, options){
        text = action.get('action')+": "+action.get("timestamp")
        var msg = $('#message');
        msg.removeClass();
        msg.html(text);
        console.log(text);
        msg.addClass(action.get("result"));
    });
});