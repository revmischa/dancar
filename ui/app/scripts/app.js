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

    });

}());


