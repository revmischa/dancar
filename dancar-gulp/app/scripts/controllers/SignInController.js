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

    $scope.alertMessage = "";

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
        if(result.success){
          $location.path('/main');
          if(!$scope.$$phase){
            $scope.$apply();
          }
        }
      }).error(function (error) {
        $scope.alertMessage = "Sorry the server is unavailable";
      });

    };

    $scope.validation = function(){
      var emailPattern = new RegExp("^([A-Za-z0-9-\+]{3,})+(\.[_A-Za-z0-9-]+)*@([A-Za-z0-9-]{3,})+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$");

      if(emailPattern.test($scope.user.mail)){
        if($scope.user.password.length > 1){
          $scope.logIn();
        }else{
          $scope.alertMessage = "Invalid Password";
          $timeout(function(){ $scope.passwordAlert = false }, 2000);
        }
      }else{
        $scope.alertMessage = "Invalid Email";
        $timeout(function(){ $scope.mailAlert = false }, 2000);
      }
    };

  });
