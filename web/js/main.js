window.Router = Backbone.Router.extend({

    routes: {
        "": "home",
        "blog": "blog"
    },

    initialize: function(){
        this.headerView = new HeaderView();
        $('.header').html(this.headerView.render().el);
    },

    home: function() {
        if(!this.homeview){
            this.homeView = new HomeView();
            this.homeView.render();
        } else {
            this.homeView.delegateEvents();
        }
        $('#content').html(this.homeView.el);
        this.headerView.select('home-menu');
    },

    blog: function() {
        if(!this.blogView){
            this.blogView = new BlogView();
            this.blogView.render();
        }  
        $('#content').html(this.blogView.el);
        this.headerView.select('blog-menu');
    },
});

templateLoader.load(['HeaderView','HomeView','BlogView'],
    function() {
        app = new Router();
        Backbone.history.start();
    });
