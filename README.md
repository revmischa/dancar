# DANCAR
## "The Uber of DanH"

```
 _____________________ 
 ����������| ������|�\\
           |  � �  |  \\         o
           |   c   |   \\        |
           |  ���  |___..\_      |
           |�������       |�``----._
           |==           _|          )
           |            /..--..      |
           |           //. - . \  == )
            \ _______// .     . \    |
   ssssss             | .  O  . |____\
 ���������������������   .   .
                           `
```

## Problem
* DanH has my car, we need to be able to summon him for rides when drunk.
* DanH needs to know our location
* We need to know DanH's location

## Approach
* Track users via smartphone apps. Simple read of GPS position, HTTP POST to update current location.
* Display users and Dancar in real-time using Google Maps API and PostGIS.

## Tasks:
[ ] Android client
[ ] iOS client
[ ] WebSocket push event support, falling back to poll-based location update
[x] Poll-based location updating
[ ] Notification system to inform users of Dancar status, and inform Dancar driver of pickup requests
