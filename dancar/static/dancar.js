var Dancar = function() {
};

$.extend(Dancar.prototype, {
    // checks to see if user is logged in and calls cb
    // cb is called with user info hash if logged in, false otherwise
    checkLoggedIn: function(cb) {
        this.getUserInfo(function(info) {
            console.log(info);
            if (! info) {
                console.error("failed to get user info API response");
                return;
            }
            cb(info.id ? info : false);
        });
    },

    getUserInfo: function(cb) {
        $.get('/api/user/info', function(res) {
            cb(res);
        });
    }
});

