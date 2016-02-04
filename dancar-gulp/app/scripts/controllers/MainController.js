'use strict';

angular.module('Dancar')
  .controller('MainController', function($scope, $location, $http, $interval, $timeout) {
    $scope.loggedIn = false;
    $scope.apiHost = 'https://dancar.herokuapp.com';
    $scope.showMap = false;
    $scope.markers = [];
    $scope.hasSetMapBounds = false;
    $scope.coords = {
      latitude: 37.79,
      longitude: -122.41,
      accuracy: 0
    };
    $scope.showStatus = true;

    $scope.markerImg = new google.maps.MarkerImage(
      "../../images/newmarker.png"
    );

    //Make globally
    $scope.alertVisible = false;
    $scope.alertMessage = '';
    $scope.showAllert = function () {
      $scope.alertVisible = true;
      $timeout(function () {
        $scope.alertVisible = false
      }, 2000);
    };
    //

    $scope.$on('$viewContentLoaded', function () {
      $scope.status = 'Initializing DanCar...';
      $scope.getCurrentPosition(true);
      //$interval(function(){ $scope.getCurrentPosition(false); },5000);
      $scope.updateLoginStatus();
      $interval(function () {
        $scope.updateLoginStatus();
      }, 10000);
      $scope.updateCarsMap();
      $interval(function () {
        $scope.updateCarsMap();
      }, 10000);
    });

    //    My refactor

    $scope.geoPositionOptions = function () {
      // enableHighAccuracy may require special permissions, could fail
      return {'enableHighAccuracy': true};
    };

    $scope.getCurrentPosition = function (drawMap) {

      if (!'geolocation' in navigator) {

        alert("You must enable geolocation to use DanCar");

        $scope.alertMessage = 'You must enable geolocation to use DanCar';
        $scope.showAllert();
      }

      var positionOptions = $scope.geoPositionOptions();

      var watchID = navigator.geolocation.getCurrentPosition(function (position) {

        //$scope.updateLatLng(position.coords.latitude, position.coords.longitude, position.coords.accuracy);            //Don`t know what is this function about

        $scope.coords.latitude = position.coords.latitude;
        $scope.coords.longitude = position.coords.longitude;
        $scope.coords.accuracy = position.coords.accuracy;

        var pos = new google.maps.LatLng($scope.coords.latitude, $scope.coords.longitude);

        $timeout(function () {
          $scope.status = 'Done';
        }, 500);
        //$scope.status = position.coords.latitude.toFixed(2) + ' ' + position.coords.longitude.toFixed(2) + ' ' + position.coords.accuracy.toFixed(2);
        $timeout(function () {
          $scope.showStatus = false;
        }, 1000);

        if (!$scope.$$phase) {
          $scope.$apply();
        }

        if (drawMap) {
          $scope.initializeMap(pos);
        } else {
          $scope.updateMarker(pos);
          console.log("Marker updated")
        }

      }, function (err) {

        $scope.status = "Don`t get location";
        // error
        if (err.code == 1) {
          // PERMISSION_DENIED
          $scope.status = 'You must grant permission for your browser to acquire your location to use DanCar';
          //alert("don`t get location - 1");
          return;
        } else if (err.code == 2) {
          // POSITION_UNAVAILABLE
          $scope.status = 'Could not determine your location';
          //alert("don`t get location - 2");
          return;
        }
      }, positionOptions);
    };

    $scope.initializeMap = function (myPos) {

      var mapId = 'map-canvas';

      var mapOptions = {
        zoom: 13,
        center: myPos,
        mapTypeId: google.maps.MapTypeId.HYBRID
      };

      $scope.map = new google.maps.Map(document.getElementById(mapId), mapOptions);
      $scope.showMap = true;

      if (!$scope.$$phase) {
        $scope.$apply();
      }

      $scope.updateMarker(myPos);
    };

    $scope.updateMarker = function (pos) {

      if (!$scope.map) return;

      if ($scope.marker) {
        $scope.marker.setPosition(pos);
      } else {
        // create new marker
        $scope.marker = new google.maps.Marker({
          'map': $scope.map,
          'position': pos,
          'draggable': false,
          'animation': google.maps.Animation.DROP
          //icon: $scope.markerImg
        });

        var win = new google.maps.InfoWindow({
          'content': "It`s Me!"
        });
        win.open($scope.map, $scope.marker);
        //$scope.map.panTo(pos);
        $scope.map.setZoom(18);
      }
    };

    $scope.updateLoginStatus = function () {
      $scope.getUserInfo(function (res) {
        if (res) {
          $scope.loggedIn = true;
          //$scope.updateUserMap();
        } else {
          $scope.loggedIn = false;
        }
      });
    };


    $scope.getUserInfo = function (callBack) {

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
          callBack(false);
          return;
        }

        callBack(info);

      }, function errorCallback(error) {
        $scope.alertMessage = 'Server not not responding';
        $scope.showAllert();
      });
    };

    //Get cars

    $scope.updateCarsMap = function () {

      $http({
        method: 'GET',
        url: $scope.apiHost + '/api/user/all'
        //url: $scope.apiHost + '/api/car/available'
      }).then(function successCallback(res) {

        //if (!res || !res.data.cars) {
        if (!res || !res.data.users) {

          alert('Did not get successful /api/user/all response');   ///////
          $scope.status = 'Failed to load DanCar users';
          return;
        }

        //var cars = res.data.cars;
        var cars = res.data.users;
        var bounds = new google.maps.LatLngBounds();

        for (var i = 0; i < cars.length; i++) {
          var car = cars[i];

          $scope.updateCarMarker(car);
          var point = $scope.getCarPoint(car);
          if (point)
            bounds.extend(point);
        }

        if (!$scope.hasSetMapBounds && bounds) {
          // position map so all dancars are visible
          $scope.hasSetMapBounds = true;
          $scope.map.panToBounds(bounds);
        }

      }, function errorCallback(error) {
        $scope.alertMessage = 'Server not not responding';
        $scope.showAllert();
      });
    };

    $scope.updateCarMarker = function (car) {

      if (!car) return;
      if (!$scope.map) return;

      var id = car.id + '';
      var pos = $scope.getCarPoint(car);

      if (!car || !id || !pos) return;

      var carMarker = $scope.markers[id];

      if (carMarker) {
        carMarker.setPosition(pos);
      } else {
        // create new marker
        carMarker = new google.maps.Marker({
          'map': $scope.map,
          'position': pos,
          'draggable': false,
          'title': car.name,
          'animation': google.maps.Animation.DROP
        });
        $scope.markers[id] = carMarker;

        var $win = document.createElement('div');

        var $carName = document.createElement('div');
        $carName.appendChild(document.createTextNode(car.name));

        //var updatedDate = new Date(car.updated_location * 1000);
        //var $dateUpdate = document.createElement('div');
        //$carName.appendChild(document.createTextNode(updatedDate));

        var $summon = document.createElement('button');
        $summon.className = 'button';
        $summon.appendChild(document.createTextNode('Summon'));

        $win.appendChild($carName);
        $win.appendChild($summon);

        //$win.append($('<div/>').text(car.name));
        //$win.append($('<div/>').text($.timeago(updatedDate)));          //Time ago jquery
        //$win.append($('<button class='btn'/>').text('Summon'));

        if (car.mobile) {

          var $callBtn = document.createElement('a');
          $callBtn.setAttribute('href', 'tel:' + car.mobile);

          var $callSubBtn = document.createElement('button');
          $callSubBtn.className = 'button call-btn';
          $callSubBtn.appendChild(document.createTextNode('Call'));

          $callBtn.appendChild($callSubBtn);

          $win.appendChild($callBtn);
        }
        var win = new google.maps.InfoWindow({
          'content': $win
        });
        win.open($scope.map, carMarker);
        $scope.map.panTo(pos);
        $scope.map.setZoom(18);
      }
    };

    $scope.getCarPoint = function (car) {

      var lng = car.lng;
      var lat = car.lat;

      if (!car || !lng || !lat) return;
      var pos = new google.maps.LatLng(Number(lat), Number(lng));
      return pos;
    };

});
