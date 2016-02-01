'use strict';

/**
 * @ngdoc function
 * @name Dancar.controller:HomeController
 * @description
 * # HomeController
 */
angular.module('Dancar')
  .controller('SignInController', function($scope, $http, $location, $timeout, $rootScope) {

    $scope.user = { mail: "", password: "" };

    $scope.mailAlert = false;
    $scope.passwordAlert = false;
    $scope.serverAlert = false;

    $scope.changeView = function(view){
      $location.path(view); // path not hash
    };

    $scope.logIn = function(){


      $http({
        method: 'POST',
        url: 'https://dancar.herokuapp.com/api/login',
        headers: {
          'Content-Type': 'application/json'

        },
        data: {
          email: $scope.user.mail,
          password: $scope.user.password
        }
      }).success(function (result) {
        alert("success")
      }).error(function (error) {
        alert("error")
      });

    };

    $scope.validation = function(){
      var emailPattern = new RegExp("^([A-Za-z0-9-\+]{3,})+(\.[_A-Za-z0-9-]+)*@([A-Za-z0-9-]{3,})+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$");

      if(emailPattern.test($scope.user.mail)){
        if($scope.user.password.length > 1){
          $scope.logIn();
        }else{
          $scope.passwordAlert = true;
          $timeout(function(){ $scope.passwordAlert = false }, 2000);
        }
      }else{
        $scope.mailAlert = true;
        $timeout(function(){ $scope.mailAlert = false }, 2000);
      }
    };

  });
