'use strict';

/**
 * @ngdoc function
 * @name Dancar.controller:MainController
 * @description
 * # MainController
 */
angular.module('Dancar')
  .controller('MainController', function($scope, $location) {

    $scope.changeView = function(view){
      $location.path(view); // path not hash
    };

    $scope.status = false;
    $scope.loggedIn = false;

    function status(msg) {
      $(".client .status.alert").text(msg).fadeIn();
    }

    var Dancar = function() {
      this.longitude = undefined;
      this.latitude  = undefined;
      this.loggedIn  = false;
      this.map       = undefined;
      this.markers   = {};
      // this.apiHost   = "http://localhost:5000";
      this.apiHost   = "https://dancar.herokuapp.com";
    };

    Dancar.prototype = {
      initClient: function() {
        status("Initializing DanCar...");
        this.initializeGeolocating(this.positionUpdated.bind(this), this.positionError.bind(this));
        this.initializeMap();
        this.updateLoginStatus();
        window.setInterval(this.updateLoginStatus.bind(this), 5000);
        window.setInterval(this.updateUserMap.bind(this), 2000);
      },

      // got updated coordinates
      positionUpdated: function(position) {
        $scope.status = true;
        status("Position updated: " + position.coords.longitude + ", " + position.coords.latitude);
      },

      positionError: function(errStr) {
        document.getElementById("status-error").innerText = errStr;
        $scope.status = false;
      },

      updateLoginStatus: function() {
        var isLoggedIn = this.loggedIn;
        var self = this;
        this.getUserInfo(function(res) {
          if (isLoggedIn && res === false) {
            $scope.loggedIn = false;
          } else if (! isLoggedIn && res) {
            $scope.loggedIn = true;
            self.updateUserMap();
          }
        });
      },

       //checks to see if user is logged in and calls cb
        // cb is called with user info hash if logged in, false otherwise
        getUserInfo: function(cb) {
          var self = this;
          $.get(this.apiHost + '/api/user/info', function(info) {
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

        $.post(this.apiHost + '/api/user/update', update, function(res) {
          // console.log("updated position");
        });
      },

      initializeMap: function(mapId) {
        if (! mapId)
          mapId = 'map-canvas';

        var mapOptions = {
          zoom: 13,
          center: new google.maps.LatLng(37.79, -122.41),
          mapTypeId: google.maps.MapTypeId.HYBRID
        };
        this.map = new google.maps.Map(document.getElementById(mapId), mapOptions);
      },

      updateMarker: function(user) {
        if (! user) return;
        if (! this.map) return;

        var id = user.id + "";
        var pos = this.getUserPoint(user);

        if (! user || ! id || ! pos) return;
        var marker = this.markers[id];

        if (marker) {
          marker.setPosition(pos);
        } else {
          // create new marker
          marker = new google.maps.Marker({
            'map': this.map,
            'position': pos,
            'draggable': false,
            'title': user.name,
            'animation': google.maps.Animation.DROP
          });
          this.markers[id] = marker;

          //var updatedDate = new Date(user.updated_location * 1000);

          //var $win = $("<div/>");                             //////////////////////////////////

          var $win = document.createElement("div");

          var $userName = document.createElement("div");
          $userName.appendChild(document.createTextNode(user.name));

          //var $dateUpdate = document.createElement("div");
          //$userName.appendChild(document.createTextNode(updatedDate));

          var $summon = document.createElement("button");
          $summon.className = "btn";
          $summon.appendChild(document.createTextNode('Summon'));

          $win.appendChild($userName);
          $win.appendChild($summon);

          //$win.append($("<div/>").text(user.name));
          //$win.append($("<div/>").text($.timeago(updatedDate)));          !!!!!!!!!!!!!!!!!!!!!!!!!!!
          //$win.append($("<button class='btn'/>").text('Summon'));
          if (user.mobile) {
            //$callBtn = $("<a/>").attr("href", "tel://" + user.mobile);
            //$callBtn.append($("<button class='btn'/>").text('Call'));

            var $callBtn = document.createElement("a");
            $callBtn.setAttribute("href", "tel://" + user.mobile);

            var $callSubBtn = document.createElement("button");
            $callSubBtn.className = "btn";
            $callSubBtn.appendChild(document.createTextNode('Call'));

            $callBtn.appendChild($callSubBtn);

            //$win.append($callBtn);
            $win.appendChild($callBtn);
          }
          var win = new google.maps.InfoWindow({
            'content': $win.get(0)
          });
          win.open(this.map, marker);
          // this.map.panTo(pos);
          // this.map.setZoom(18);
        }
      },

      // call to fetch all user locations and update the map markers
      updateUserMap: function() {
        if (! this.map) return;
        if (! this.loggedIn) return;

        $.get(this.apiHost + '/api/user/all', function(res){
          if (! res || ! res.users) {
            console.log("Did not get successful /api/user/all response");
            status("Failed to load DanCar users");
            return;
          }

          var users = res.users;
          var bounds = new google.maps.LatLngBounds();
          for (i in users) {
            var user = users[i];
            this.updateMarker(user);
            var point = this.getUserPoint(user);
            if (point)
              bounds.extend(point);
          }

          if (! this.hasSetMapBounds && bounds) {
            // position map so all dancars are visible
            this.hasSetMapBounds = true;
            this.map.panToBounds(bounds);
          }
        });
      },

      getUserPoint: function(user) {
        var lng = user.lng;
        var lat = user.lat;

        if (! user || ! lng || ! lat) return;
        var pos = new google.maps.LatLng(Number(lat), Number(lng));
        return pos;
      }
    };

    $scope.dc = new Dancar();
    $scope.dc.initClient();

  });
