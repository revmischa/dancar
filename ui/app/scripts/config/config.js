'use strict';

angular.module('Dancar').config(function ($routeProvider, $httpProvider) {
  // register $http interceptors, if any. e.g.
  // $httpProvider.interceptors.push('interceptor-name');
  $httpProvider.defaults.withCredentials = true;

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

