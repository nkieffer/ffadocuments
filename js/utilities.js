$(function(){
    document.clearMessage = function(){
        var msg = $('#message');
        msg.removeClass();
        msg.empty();
    }
    document.clearMain = function(){
        $('#main').empty();
    }

    document.fetchTemplate = function(template, model, callback) {
        $('#main').html('Loading...');
        if (document.router.templates[template] === null){
            console.log("fetching ", template)
            $.ajax({
                url: "views/"+template+".html",
                success: function(tmp, status, xhr){
                    document.router.templates[template] = _.template(tmp);
                    $('#main').html(document.router.templates[template](model))
                    console.dir(callback);
                    callback(); 
                }
            });
        } else {                 
            $('#main').html(document.router.templates[template](model))
            console.dir(callback);
            callback(); 
        }
    }
})