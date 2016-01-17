var app = {
    // Application Constructor
    initialize: function() {
        this.bindEvents();
        this.initClient();
    },

    initClient: function() {
        status("Initializing DanCar...");
        this.dc = new Dancar();
        this.dc.initializeMap();
        this.dc.initializeGeolocating(positionUpdated, positionError);
        updateLoginStatus();
        window.setInterval(updateLoginStatus, 5000);
        window.setInterval(updateUserMap, 2000);
    },
    // Bind Event Listeners
    //
    // Bind any events that are required on startup. Common events are:
    // 'load', 'deviceready', 'offline', and 'online'.
    bindEvents: function() {
        document.addEventListener('deviceready', this.onDeviceReady, false);
    },
    // deviceready Event Handler
    //
    // The scope of 'this' is the event. In order to call the 'receivedEvent'
    // function, we must explicitly call 'app.receivedEvent(...);'
    onDeviceReady: function() {
        app.receivedEvent('deviceready');
    },
    // Update DOM on a Received Event
    receivedEvent: function(id) {
        var parentElement = document.getElementById(id);
        var listeningElement = parentElement.querySelector('.listening');
        var receivedElement = parentElement.querySelector('.received');

        listeningElement.setAttribute('style', 'display:none;');
        receivedElement.setAttribute('style', 'display:block;');

        console.log('Received Event: ' + id);
    },

    // got updated coordinates
    positionUpdated: function(position) {
        $(".client .error.alert").hide();
        status("Position updated: " + position.coords.longitude + ", " + position.coords.latitude);
    },

    positionError: function(errStr) {
        $(".client .error.alert").text(errStr).fadeIn();
    },

    loggedIn: function() {
        $(".client .not-logged-in").hide();
        $(".client .logged-in").fadeIn();
    },

    notLoggedIn: function() {
        $(".client .logged-in").hide();
        $(".client .not-logged-in").fadeIn();            
    },

    updateLoginStatus: function() {
        var isLoggedIn = this.dc.loggedIn;
        this.dc.getUserInfo(function(res) {
            if (isLoggedIn && res === false) {
                notLoggedIn();
            } else if (! isLoggedIn && res) {
                loggedIn();
                updateUserMap();
            }
        });
    },

    updateUserMap: function() {
        this.dc.updateUserMap();
    }
};

app.initialize();

/*********************************/

status: function(msg) {
    $(".client .status.alert").text(msg).fadeIn();
},

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

    geoPositionOptions: function() {
        // enableHighAccuracy may require special permissions, could fail
        return { 'enableHighAccuracy': true };
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
        var positionOptions = this.geoPositionOptions();
        var watchID = navigator.geolocation.watchPosition(function(position) {
            // console.log("got new position: " + position.coords.latitude + ", " + position.coords.longitude);
            self.updateLatLng(position.coords.latitude, position.coords.longitude, position.coords.accuracy);
            // console.log(position);
            if (updatecb)
                updatecb(position);
        }, function(err) {
            // error
            if (err.code == 1) {
                // PERMISSION_DENIED
                if (errorcb)
                    errorcb("You must grant permission for your browser to acquire your location to use DanCar");
                return;
            } else if (err.code == 2) {
                // POSITION_UNAVAILABLE
                if (errorcb)
                    errorcb("Could not determine your location");
                return;
            } // ...
        }, positionOptions);

        this.locWatchID = watchID;
    },

    // set new lng/lat for the current user
    updateLatLng: function(lat, lng, accuracy_meters) {
        // ideally we would retry later if not logged in when this is called
        if (! this.loggedIn)
            return;

        if (! lat && ! lng) {
            // yes technically speaking these could be zero... whatever
            console.log("updateLatLng called with no lat/lng");
            return;
        }

        var update = {
            'lat': lat,
            'lng': lng
        };

        if (accuracy_meters)
            update.location_accuracy_meters = accuracy_meters;

        $.post('/api/user/update', update, function(res) {
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
        console.log(Number(lat) + " + " + Number(lng));

        if (! user || ! id || ! lng || ! lat) return;
        var marker = this.markers[id];
        var pos = new google.maps.LatLng(Number(lat), Number(lng));

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
            $win.append($("<button class='btn'/>").text('Summon'));
            if (user.mobile) {
                $callBtn = $("<a/>").attr("href", "tel://" + user.mobile);
                $callBtn.append($("<button class='btn'/>").text('Call'));
                $win.append($callBtn);
            }
            var win = new google.maps.InfoWindow({
                'content': $win.get(0)
            });
            win.open(this.map, marker);
            this.map.panTo(pos);
            this.map.setZoom(18);
        }
    }
});

