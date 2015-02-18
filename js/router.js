$(document).ready(function() {
    Backbone.Events.on("request", function(model, xhr, opts) {
        console.dir(model);
    });
    var Router = Backbone.Router.extend({
        routes: {
            "home": "home",
            "partners": "partnerTable",
            "partners/form(/:id)": "partnerForm",
            "partners/delete/:id": "partnerDelete",
            "partners/json(/:id)": "partnerJSON",
            "projects": "projectTable",
            "projects/form(/:id)": "projectForm",
            "projects/json(/:id)": "projectJSON",
            "volunteers": "volunteerList",
            "assignments": "assignmentList",
            "invoices": "invoiceList"
        },
        templates: {
            partnerTableTemp: null,
            partnerFormTemp: _.template($("#partnerFormTemp").html()),
            projectTableTemp: _.template($('#projectTableTemp').html()),
            projectFormTemp: _.template($('#projectFormTemp').html()),
        },
        home: function() {

        },
        partnerTable: function() {
            var router = this
            document.fetchTemplate('partnerTableTemp', null, function(){ document.partnerCollection.renderTable();})
        },
        partnerForm: function(key) {
            var router=this;
            document.clearMessage();
            var action, partner;
            if (key === null) {
                partner = {id: "",name: "",abbr: "",address: "",comment: ""};
            } else {
                partner = document.partnerCollection.get(key).attributes;
            }
            document.fetchTemplate('partnerFormTemp', partner, function() {
           // $('#main').html(this.templates.partnerForm(partner));
                $('#partnerForm').submit(function() {
                    var id = $('#id').attr('value');
                    var name = $('#name').attr('value');
                    var abbr = $('#abbr').attr('value');
                    var address = $('#address').attr('value');
                    var comment = $('#comment').attr('value');
                    if (id !== "") {
                        var partner = document.partnerCollection.get(id);
                    } else {
                        var partner = new document.PartnerModel();
                  /*      partner.on({
                            "change": partner.changeAction,
                            "destroy": partner.deleteAction
                        });*/
                        document.partnerCollection.add([partner]);
                    }
                    partner.set({name: name,abbr: abbr,address: address,comment: comment})
                    partner.save(null,{
                        success: function(mdl, response, options) {
                            if (mdl.isNew()){

                                mdl.set('id', response);
                            }
                            window.location.hash="partners";  
                        },
                        error: function(model, response, options) {
                            console.dir(response);
                        }
                    });
                    return false;
                });
            })
        },
        partnerDelete: function(id) {
            var router = this;
            var partner = document.partnerCollection.get(id);
            partner.destroy({ 
                success: function (model, response, options) {

                    document.actionCollection.add({ 
                        action: "Partner deleted.", 
                        result: "success",
                        timestamp: new Date() 
                    });
                    window.location.hash = "partners";

                },
                error: function (model, response, options) {
                    document.actionCollection.add({ 
                        action: "Partner not deleted", 
                        result: "error",
                        timestamp: new Date()
                    });
                }
            });
        },
        partnerJSON: function(key) {
            
        },
        projectTable: function() {
            $('#main').html(this.templates.projectTable(null));
        },
        projectForm: function(id) {
            var router=this;
            document.clearMessage();
            var action, partner;
            if (id === null) {
                project = {id: "",name: "",abbr: "",price: "",additionalWeekPrice: "", minimumDuration: "", comment: ""};
            } else {
                project = document.projectCollection.get(id).attributes;
            }
 
            $('#main').html(this.templates.projectForm(project));
        },
        projectJSON: function(key) {
           
        },
        volunteerList: function() {
            
        },
        invoiceList: function() {
           
        }
    });
    document.router = new Router();
    document.router.on("route", function(route, params) {
        console.log("Route: "+route + ": " +params);
        $('#page').html(route);
    });
    Backbone.history.start()

});
