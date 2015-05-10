var Dancar = function() {
    this.longitude = undefined;
    this.latitude  = undefined;
    this.loggedIn  = false;
    this.map       = undefined;
    this.markers   = {};
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

    // call to fetch all user locations and update the map markers
    updateUserMap: function() {
        var self = this;

        if (! this.map) return;
        if (! this.loggedIn) return;

        $.get('/api/user/all', function(res) {
            if (! res || ! res.users) {
                console.log("Did not get successful /api/user/all response");
                return;
            }

            var users = res.users;
            for (i in users) {
                var user = users[i];
                self.updateMarker(user);
            }
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
            // self.updateLatLng(position.coords.latitude, position.coords.longitude);
            // console.log(position);
            if (updatecb)
                updatecb(position);
        });

        this.locWatchID = watchID;
    },

    // set new lng/lat for the current user
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
    },

    initializeMap: function(mapId) {
        if (! mapId)
            mapId = 'map-canvas';

        var mapOptions = {
            zoom: 14,
            center: new google.maps.LatLng(37.88, -122.26),
            mapTypeId: google.maps.MapTypeId.HYBRID
        };
        this.map = new google.maps.Map(document.getElementById(mapId), mapOptions);
    },

    updateMarker: function(user) {
        if (! user) return;
        if (! this.map) return;

        var id = user.id + "";
        var lng = user.lng;
        var lat = user.lat;

        if (! user || ! id || ! lng || ! lat) return;
        var marker = this.markers[id];
        var pos = new google.maps.LatLng(lat, lng);

        if (marker) {
            marker.setPosition(pos);
        } else {
            // create new marker
            marker = new google.maps.Marker({
                'map': this.map,
                'position': pos,
                'draggable': false,
                'title': user.name
            });
            this.markers[id] = marker;

            var updatedDate = new Date(user.updated_location * 1000);

            var $win = $("<div/>");
            
            $win.append($("<div/>").text(user.name));
            $win.append($("<div/>").text($.timeago(updatedDate)));
            var win = new google.maps.InfoWindow({
                'content': $win.get(0)
            });
            win.open(this.map, marker);
            this.map.panTo(pos);
            this.map.setZoom(18);
        }
    }
});

