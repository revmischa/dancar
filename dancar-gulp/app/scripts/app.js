'use strict';

/**
 * @ngdoc overview
 * @name Dancar
 * @description
 * # Initializes main application and routing
 *
 * Main module of the application.
 */



(function () {
  angular.module('Dancar', ['ionic', 'ngCordova', 'ngResource','ngRoute'])

    .run(function ($ionicPlatform) {
      $ionicPlatform.ready(function () {
        // save to use plugins here
      });

      // add possible global event handlers here

    })

    .config(function ($routeProvider) {
      // register $http interceptors, if any. e.g.
      // $httpProvider.interceptors.push('interceptor-name');

      $routeProvider
        .when('/sign', {
          templateUrl: 'templates/views/sign_in.html',
          controller: 'SignInController'
        })

        .when('/main', {
          templateUrl: 'templates/views/main.html',
          controller: 'MainController'
        })
        .  otherwise({
          redirectTo: '/sign'
        });

    });

}());


