//This template loader used to asynchronously load templates in separate .html files
window.templateLoader = {
    load: function(views, callback) {
        var deferreds = [];
        $.each(view,function(index,view) {
            if(window[view]) {
                deferreds.push($.get('template/'+view+'.html',function(data){
                    window[view].prototype.template = _.template(data);
                }, 'html'));
            }else{
                alert(view+" not found");
            }
        });

        $.when.apply(null, deferreds).done(callback);
    }
}
