var Dancar = function() {
    this.longitude = undefined;
    this.latitude  = undefined;
    this.loggedIn  = false;
};

$.extend(Dancar.prototype, {    
    // checks to see if user is logged in and calls cb
    // cb is called with user info hash if logged in, false otherwise
    getUserInfo: function(cb) {
        var self = this;
        $.get('/api/user/info', function(info) {
            if (! info) {
                console.error("failed to get user info API response");
                return;
            }
            if (! info.id) {
                // not logged in
                self.loggedIn = false;
                cb(false);
                return;
            }

            // logged in
            self.loggedIn = true;
            cb(info);
        });
    },

    // start tracking/updating position
    initializeGeolocating: function(updatecb, errorcb) {
        var self = this;

        if (this.locWatchID) {
            console.log("initializeGeolocating called but watchID is set");
            return;
        }

        // make sure geolocating is available/enabled
        if (! "geolocation" in navigator) {
            // can't geolocate
            if (errorcb) 
                errorcb("You must enable geolocation to use DanCar");
            return;
        }

        // start watching location
        var watchID = navigator.geolocation.watchPosition(function(position) {
            // console.log("got new position: " + position.coords.latitude + ", " + position.coords.longitude);
            self.updateLatLng(position.coords.latitude, position.coords.longitude);
            if (updatecb)
                updatecb(position);
        });

        this.locWatchID = watchID;
    },

    updateLatLng: function(lat, lng) {
        // ideally we would retry later if not logged in when this is called
        if (! this.loggedIn)
            return;

        if (! lat && ! lng) {
            // yes technically speaking these could be zero... whatever
            console.log("updateLatLng called with no lat/lng");
            return;
        }

        $.post('/api/user/update', {
            'lat': lat,
            'lng': lng
        }, function(res) {
            // console.log("updated position");
        });
    }
});

