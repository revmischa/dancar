'use strict';

angular.module('Dancar')
  .controller('MainController', function($scope, $location, $http, $interval, $timeout) {
    $scope.loggedIn = false;
    $scope.apiHost = 'https://dancar.herokuapp.com';
    $scope.map = undefined;
    $scope.showMap = false;
    $scope.status = '';
    $scope.markers = {};
    $scope.hasSetMapBounds = false;
    $scope.coords = {
      latitude: 37.79,
      longitude: -122.41,
      accuracy: 0
    };

    $scope.markerImg = new google.maps.MarkerImage(
      "../../images/newmarker.png"
    );

    //Make globally

    $scope.alertMessage = '';
    $scope.alertVisible = false;
    $scope.showAllert = function(){
      $scope.alertVisible = true;
      $timeout(function(){ $scope.alertVisible = false }, 2000);
    };
    //

    $scope.$on('$viewContentLoaded',function(){
      $scope.status = 'Initializing DanCar...';
      $scope.initializeGeolocating();

      $scope.updateLoginStatus();

      //$interval(function(){$scope.updateLoginStatus()},5000);
      //$interval(function(){$scope.updateUserMap},2000);
    });

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

        alert("You must enable geolocation to use DanCar");

        $scope.alertMessage = 'You must enable geolocation to use DanCar';
        $scope.showAllert();
      }
      // start watching location
      var positionOptions = $scope.geoPositionOptions();

      var watchID = navigator.geolocation.watchPosition(function (position) {

        $scope.updateLatLng(position.coords.latitude, position.coords.longitude, position.coords.accuracy);            //Don`t know what is this function about

        $scope.coords.latitude = position.coords.latitude;
        $scope.coords.longitude = position.coords.longitude;
        $scope.coords.accuracy = position.coords.accuracy;
        $scope.status= '';
        $scope.status = position.coords.latitude.toFixed(2) + ' ' + position.coords.longitude.toFixed(2) + ' ' + position.coords.accuracy.toFixed(2);

        if(!$scope.$$phase){
          $scope.$apply();
        }

      }, function (err) {

        alert("don`t get location");
        // error
        if (err.code == 1) {
          // PERMISSION_DENIED
          $scope.status = 'You must grant permission for your browser to acquire your location to use DanCar';
          alert("don`t get location - 1");
          return;
        } else if (err.code == 2) {
          // POSITION_UNAVAILABLE
          $scope.status = 'Could not determine your location';
          alert("don`t get location - 2");
          return;
        }
      }, positionOptions);

      $scope.locWatchID = watchID;
      $scope.initializeMap('map-canvas');

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

    $scope.initializeMap = function(mapId) {
      if (!mapId)
        mapId = 'map-canvas';

      console.log($scope.coords.latitude);
      console.log($scope.coords.longitude);

      var mapOptions = {
        zoom: 13,
        center: new google.maps.LatLng($scope.coords.latitude, $scope.coords.longitude),
        mapTypeId: google.maps.MapTypeId.HYBRID
      };

      $scope.map = new google.maps.Map(document.getElementById(mapId), mapOptions);

      $scope.showMap = true;

      var markerPos = new google.maps.LatLng($scope.coords.latitude, $scope.coords.longitude);

      var marker = new google.maps.Marker({
        'map': $scope.map,
        'position': markerPos,
        'draggable': false,
        'title': 'Me',
        'animation': google.maps.Animation.DROP,
        icon: $scope.markerImg
      });

      marker.setMap($scope.map);

      var win = new google.maps.InfoWindow({
        'content': "It`s Me!"
      });
      win.open($scope.map, marker);
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
          alert('failed to get user info API response');  ////////
          return;
        }
        if (!info.data.id) {
          // not logged in
          alert('User is not logged in');   /////////
          $scope.loggedIn = false;
          cb(false);
          return;
        }

        $scope.loggedIn = true;
        cb(info);

      }, function errorCallback(error) {
        alert('Server not not responding');   //////
      });
    };

    // call to fetch all user locations and update the map markers
    $scope.updateUserMap = function(){

      $http({
        method: 'GET',
        url: $scope.apiHost + '/api/user/all'
      }).then(function successCallback(res) {

        if (!res || !res.data.users) {

          alert('Did not get successful /api/user/all response');   ///////
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
        }

      }, function errorCallback(error) {
        alert('Server not not responding');   //////
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
        $summon.className = 'button';
        $summon.appendChild(document.createTextNode('Summon'));

        $win.appendChild($userName);
        $win.appendChild($summon);

        //$win.append($('<div/>').text(user.name));
        //$win.append($('<div/>').text($.timeago(updatedDate)));          //Time ago jquery
        //$win.append($('<button class='btn'/>').text('Summon'));
        if(user.mobile) {

          var $callBtn = document.createElement('a');
          $callBtn.setAttribute('href', 'tel:' + user.mobile);

          var $callSubBtn = document.createElement('button');
          $callSubBtn.className = 'button call-btn';
          $callSubBtn.appendChild(document.createTextNode('Call'));

          $callBtn.appendChild($callSubBtn);

          $win.appendChild($callBtn);
        }
        var win = new google.maps.InfoWindow({
          'content': $win
        });
        win.open($scope.map, marker);
        //$scope.map.panTo(pos);
        $scope.map.setZoom(18);
      }
    };

    $scope.getUserPoint = function(user) {

      var lng = user.lng;
      var lat = user.lat;

      if (!user || !lng || !lat) return;
      var pos = new google.maps.LatLng(Number(lat), Number(lng));
      return pos;
    };

  });
