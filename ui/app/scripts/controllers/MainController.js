'use strict';

angular.module('Dancar')
  .controller('MainController', function($scope, $location, $http,$interval) {
    $scope.loggedIn = false;
    $scope.apiHost = 'https://dancar.herokuapp.com';
    $scope.map = undefined;
    $scope.showMap = false;
    $scope.status = '';
    $scope.markers = {};
    $scope.hasSetMapBounds = false;

    $scope.$on('$viewContentLoaded',function(){
      $scope.status = 'Initializing DanCar...';
      $scope.initializeMap();
      $scope.initializeGeolocating();
      $scope.updateLoginStatus();

      //$interval(function(){$scope.updateLoginStatus()},5000);
      //$interval(function(){$scope.updateUserMap},2000);

      //this.initializeGeolocating(this.positionUpdated.bind(this), this.positionError.bind(this));
      //this.initializeMap();
      //this.updateLoginStatus();
      //window.setInterval(this.updateLoginStatus.bind(this), 5000);
      //window.setInterval(this.updateUserMap.bind(this), 2000);
    });

    $scope.initializeMap = function(mapId) {
      if (!mapId)
        mapId = 'map-canvas';

      var mapOptions = {
        zoom: 13,
        center: new google.maps.LatLng(37.79, -122.41),
        mapTypeId: google.maps.MapTypeId.HYBRID
      };
      $scope.map = new google.maps.Map(document.getElementById(mapId), mapOptions);

      $scope.showMap = true;

      if(!$scope.$$phase){
        $scope.$apply();
      }

    };

    $scope.updateLoginStatus = function(){
      $scope.getUserInfo(function(res) {
        if (res) {
          $scope.loggedIn = true;
          $scope.updateUserMap();
        }else{
          $scope.loggedIn = false;
        }
      });
    };

    //checks to see if user is logged in and calls cb
    // cb is called with user info hash if logged in, false otherwise
    $scope.getUserInfo =  function(cb){

      $http({
        method: 'GET',
        url: $scope.apiHost + '/api/user/info'
      }).then(function successCallback(info) {
        if (!info) {
          alert('failed to get user info API response');  ////////////////////////////////////////////////
          return;
        }
        if (!info.data.id) {
          //for(var i in info.data){
          //  alert(i + ': ' + info.data[i]);
          //}
          // not logged in
          alert('User is not logged in');   ////////////////////////////////////////////////
          $scope.loggedIn = false;
          cb(false);
          return;
        }

        $scope.loggedIn = true;
        cb(info);

      }, function errorCallback(error) {
        alert('Server not not responding');   ////////////////////////////////////////////////
      });
    };

    // call to fetch all user locations and update the map markers
    $scope.updateUserMap = function(){

      $http({
        method: 'GET',
        url: $scope.apiHost + '/api/user/all'
      }).then(function successCallback(res) {

        if (!res || !res.data.users) {

          alert('Did not get successful /api/user/all response');   ////////////////////////////////////////////////
          $scope.status = 'Failed to load DanCar users';
          return;
        }

        var users = res.data.users;
        var bounds = new google.maps.LatLngBounds();
        for (var i in users) {
          var user = users[i];

          $scope.updateMarker(user);
          var point = $scope.getUserPoint(user);
          if (point)
            bounds.extend(point);
        }

        if (!$scope.hasSetMapBounds && bounds) {
          // position map so all dancars are visible
          $scope.hasSetMapBounds = true;

          $scope.map.panToBounds(bounds);

          alert('End adding users');
        }

      }, function errorCallback(error) {
        alert('Server not not responding');   ////////////////////////////////////////////////
      });
    };

    $scope.updateMarker = function(user) {

      if(!user) return;
      if(!$scope.map) return;

      var id = user.id + '';
      var pos = $scope.getUserPoint(user);

      if (!user || !id || !pos) return;

      var marker = $scope.markers[id];

      if (marker) {
        marker.setPosition(pos);
      } else {
        // create new marker
        marker = new google.maps.Marker({
          'map': $scope.map,
          'position': pos,
          'draggable': false,
          'title': user.name,
          'animation': google.maps.Animation.DROP
        });
        $scope.markers[id] = marker;

        var $win = document.createElement('div');

        var $userName = document.createElement('div');
        $userName.appendChild(document.createTextNode(user.name));

        //var updatedDate = new Date(user.updated_location * 1000);
        //var $dateUpdate = document.createElement('div');
        //$userName.appendChild(document.createTextNode(updatedDate));

        var $summon = document.createElement('button');
        $summon.className = 'btn';
        $summon.appendChild(document.createTextNode('Summon'));

        $win.appendChild($userName);
        $win.appendChild($summon);

        //$win.append($('<div/>').text(user.name));
        //$win.append($('<div/>').text($.timeago(updatedDate)));          //Time ago jquery
        //$win.append($('<button class='btn'/>').text('Summon'));
        if(user.mobile) {

          var $callBtn = document.createElement('a');
          $callBtn.setAttribute('href', 'tel://' + user.mobile);

          var $callSubBtn = document.createElement('button');
          $callSubBtn.className = 'btn';
          $callSubBtn.appendChild(document.createTextNode('Call'));

          $callBtn.appendChild($callSubBtn);

          $win.appendChild($callBtn);
        }
        var win = new google.maps.InfoWindow({
          //'content': $win.get(0)                    //!!!!!!!!!!!!!!!!!!!!!!!!!!!!
          'content': $win                             //!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        });
        win.open($scope.map, marker);
        // this.map.panTo(pos);
        // this.map.setZoom(18);
      }
    };

    $scope.getUserPoint = function(user) {

      var lng = user.lng;
      var lat = user.lat;

      if (!user || !lng || !lat) return;
      var pos = new google.maps.LatLng(Number(lat), Number(lng));
      return pos;
    };

    $scope.geoPositionOptions = function() {
      // enableHighAccuracy may require special permissions, could fail
      return { 'enableHighAccuracy': true };
    };

    // start tracking/updating position
    $scope.initializeGeolocating = function() {

      if ($scope.locWatchID) {
        alert('initializeGeolocating called but watchID is set');
        return;
      }

      // make sure geolocating is available/enabled
      if (!'geolocation' in navigator) {
        // can't geolocate
        if (errorcb)
          errorcb('You must enable geolocation to use DanCar');
        return;
      }

      // start watching location
      var positionOptions = $scope.geoPositionOptions();

      var watchID = navigator.geolocation.watchPosition(function(position) {

        $scope.updateLatLng(position.coords.latitude, position.coords.longitude, position.coords.accuracy);

        $scope.status = position.coords.latitude + ' ' + position.coords.longitude + ' ' +  position.coords.accuracy;

      }, function(err) {
        // error
        if (err.code == 1) {
          // PERMISSION_DENIED
            $scope.status = 'You must grant permission for your browser to acquire your location to use DanCar';
            return;
        } else if (err.code == 2) {
          // POSITION_UNAVAILABLE
            $scope.status = 'Could not determine your location';
            return;
        } // ...
      }, positionOptions);

      $scope.locWatchID = watchID;
    };

    $scope.updateLatLng = function(lat, lng, accuracy_meters) {
      // ideally we would retry later if not logged in when this is called
      if (!$scope.loggedIn)
        return;

      if (!lat && !lng) {
        // yes technically speaking these could be zero... whatever
        alert('updateLatLng called with no lat/lng');
        return;
      }

      var update = {
        'lat': lat,
        'lng': lng
      };

      if (accuracy_meters)
        update.location_accuracy_meters = accuracy_meters;

        $http({
          method: 'POST',
          url: $scope.apiHost + '/api/user/update',
          headers: {
            'Content-Type': 'application/json'
          },
          data: update
        }).success(function (result) {
          if(result.data.msg = 'Location updated.'){            //!!!!  Include data
            alert('updated position');
          }
        }).error(function (error) {
          alert('Sorry the server is unavailable');
        });
    };

});

  //  var Dancar = function() {
  //    this.longitude = undefined;
  //    this.latitude  = undefined;
  //    this.loggedIn  = false;
  //    this.map       = undefined;
  //    this.markers   = {};
  //    // this.apiHost   = 'http://localhost:5000';
  //    this.apiHost   = 'https://dancar.herokuapp.com';
  //  };
  //
  //  Dancar.prototype = {
  //    initClient: function() {
  //      status('Initializing DanCar...');
  //      this.initializeGeolocating(this.positionUpdated.bind(this), this.positionError.bind(this));
  //      this.initializeMap();
  //      this.updateLoginStatus();
  //      window.setInterval(this.updateLoginStatus.bind(this), 5000);
  //      window.setInterval(this.updateUserMap.bind(this), 2000);
  //    },
  //
  //    // got updated coordinates
  //    positionUpdated: function(position) {
  //      $scope.status = true;
  //      status('Position updated: ' + position.coords.longitude + ', ' + position.coords.latitude);
  //    },
  //
  //    positionError: function(errStr) {
  //      document.getElementById('status-error').innerText = errStr;
  //      $scope.status = false;
  //    },
  //
  //    updateLoginStatus: function() {
  //      var isLoggedIn = this.loggedIn;
  //      var self = this;
  //      this.getUserInfo(function(res) {
  //        if (isLoggedIn && res === false) {
  //          $scope.loggedIn = false;
  //        } else if (! isLoggedIn && res) {
  //          $scope.loggedIn = true;
  //          self.updateUserMap();
  //        }
  //      });
  //    },
  //
  //
  //    geoPositionOptions: function() {
  //      // enableHighAccuracy may require special permissions, could fail
  //      return { 'enableHighAccuracy': true };
  //    },
  //
  //    // start tracking/updating position
  //    initializeGeolocating: function(updatecb, errorcb) {
  //      var self = this;
  //
  //      if (this.locWatchID) {
  //        console.log('initializeGeolocating called but watchID is set');
  //        return;
  //      }
  //
  //      // make sure geolocating is available/enabled
  //      if (! 'geolocation' in navigator) {
  //        // can't geolocate
  //        if (errorcb)
  //          errorcb('You must enable geolocation to use DanCar');
  //        return;
  //      }
  //
  //      // start watching location
  //      var positionOptions = this.geoPositionOptions();
  //      var watchID = navigator.geolocation.watchPosition(function(position) {
  //        // console.log('got new position: ' + position.coords.latitude + ', ' + position.coords.longitude);
  //        self.updateLatLng(position.coords.latitude, position.coords.longitude, position.coords.accuracy);
  //
  //        // console.log(position);
  //        if (updatecb)
  //          updatecb(position);
  //      }, function(err) {
  //        // error
  //        if (err.code == 1) {
  //          // PERMISSION_DENIED
  //          if (errorcb)
  //            errorcb('You must grant permission for your browser to acquire your location to use DanCar');
  //          return;
  //        } else if (err.code == 2) {
  //          // POSITION_UNAVAILABLE
  //          if (errorcb)
  //            errorcb('Could not determine your location');
  //          return;
  //        } // ...
  //      }, positionOptions);
  //
  //      this.locWatchID = watchID;
  //    },
  //
  //    // set new lng/lat for the current user
  //    updateLatLng: function(lat, lng, accuracy_meters) {
  //      // ideally we would retry later if not logged in when this is called
  //
  //      if (! this.loggedIn)
  //        return;
  //
  //      if (! lat && ! lng) {
  //        // yes technically speaking these could be zero... whatever
  //        console.log('updateLatLng called with no lat/lng');
  //        return;
  //      }
  //
  //      var update = {
  //        'lat': lat,
  //        'lng': lng
  //      };
  //
  //      if (accuracy_meters)
  //        update.location_accuracy_meters = accuracy_meters;
  //
  //      $.post(this.apiHost + '/api/user/update', update, function(res) {
  //        // console.log('updated position');
  //      });
  //    },
  //
  //    initializeMap: function(mapId) {
  //      if (! mapId)
  //        mapId = 'map-canvas';
  //
  //      var mapOptions = {
  //        zoom: 13,
  //        center: new google.maps.LatLng(37.79, -122.41),
  //        mapTypeId: google.maps.MapTypeId.HYBRID
  //      };
  //      this.map = new google.maps.Map(document.getElementById(mapId), mapOptions);
  //    },
  //
  //    updateMarker: function(user) {
  //      if (! user) return;
  //      if (! this.map) return;
  //
  //      var id = user.id + ';
  //      var pos = this.getUserPoint(user);
  //
  //      if (! user || ! id || ! pos) return;
  //      var marker = this.markers[id];
  //
  //      if (marker) {
  //        marker.setPosition(pos);
  //      } else {
  //        // create new marker
  //        marker = new google.maps.Marker({
  //          'map': this.map,
  //          'position': pos,
  //          'draggable': false,
  //          'title': user.name,
  //          'animation': google.maps.Animation.DROP
  //        });
  //        this.markers[id] = marker;
  //
  //        //var updatedDate = new Date(user.updated_location * 1000);
  //
  //        //var $win = $('<div/>');                             //////////////////////////////////
  //
  //        var $win = document.createElement('div');
  //
  //        var $userName = document.createElement('div');
  //        $userName.appendChild(document.createTextNode(user.name));
  //
  //        //var $dateUpdate = document.createElement('div');
  //        //$userName.appendChild(document.createTextNode(updatedDate));
  //
  //        var $summon = document.createElement('button');
  //        $summon.className = 'btn';
  //        $summon.appendChild(document.createTextNode('Summon'));
  //
  //        $win.appendChild($userName);
  //        $win.appendChild($summon);
  //
  //        //$win.append($('<div/>').text(user.name));
  //        //$win.append($('<div/>').text($.timeago(updatedDate)));          !!!!!!!!!!!!!!!!!!!!!!!!!!!
  //        //$win.append($('<button class='btn'/>').text('Summon'));
  //        if (user.mobile) {
  //          //$callBtn = $('<a/>').attr('href', 'tel://' + user.mobile);
  //          //$callBtn.append($('<button class='btn'/>').text('Call'));
  //
  //          var $callBtn = document.createElement('a');
  //          $callBtn.setAttribute('href', 'tel://' + user.mobile);
  //
  //          var $callSubBtn = document.createElement('button');
  //          $callSubBtn.className = 'btn';
  //          $callSubBtn.appendChild(document.createTextNode('Call'));
  //
  //          $callBtn.appendChild($callSubBtn);
  //
  //          //$win.append($callBtn);
  //          $win.appendChild($callBtn);
  //        }
  //        var win = new google.maps.InfoWindow({
  //          'content': $win.get(0)
  //        });
  //        win.open(this.map, marker);
  //        // this.map.panTo(pos);
  //        // this.map.setZoom(18);
  //      }
  //    },
  //
  //    // call to fetch all user locations and update the map markers
  //    updateUserMap: function() {
  //      if (! this.map) return;
  //      if (! this.loggedIn) return;
  //
  //      $.get(this.apiHost + '/api/user/all', function(res){
  //        if (! res || ! res.users) {
  //          console.log('Did not get successful /api/user/all response');
  //          status('Failed to load DanCar users');
  //          return;
  //        }
  //
  //        var users = res.users;
  //        var bounds = new google.maps.LatLngBounds();
  //        for (i in users) {
  //          var user = users[i];
  //          this.updateMarker(user);
  //          var point = this.getUserPoint(user);
  //          if (point)
  //            bounds.extend(point);
  //        }
  //
  //        if (! this.hasSetMapBounds && bounds) {
  //          // position map so all dancars are visible
  //          this.hasSetMapBounds = true;
  //          this.map.panToBounds(bounds);
  //        }
  //      });
  //    },
  //
  //    getUserPoint: function(user) {
  //      var lng = user.lng;
  //      var lat = user.lat;
  //
  //      if (! user || ! lng || ! lat) return;
  //      var pos = new google.maps.LatLng(Number(lat), Number(lng));
  //      return pos;
  //    }
  //  };
  //
  //  $scope.dc = new Dancar();
  //  $scope.dc.initClient();
  //
  //});
