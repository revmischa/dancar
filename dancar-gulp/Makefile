.PHONY: init init-node init-bower build init-cordova

# set up everything from scratch
init: init-node init-bower init-cordova build

init-node:
	npm install

init-bower:
	bower install

build:
	gulp -b

init-cordova:
	cordova plugin add cordova-plugin-geolocation@1.0.0
	cordova plugin add https://github.com/apache/cordova-plugin-whitelist.git 

droid:
	cordova run android
