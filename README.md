# netmanager
Amateur Radio Net Control Software for severe weather and rag chew nets.  Designed specifically for the needs of the Lawton Independent Repeater Alliance.

http://www.wx5law.org

This software can be deployed using docker containers.

First build the netmanager image itself:

sudo docker built -t netmanager .

then use docker-compose to deploy it on your docker host:

docker-deploy up -d

You'll need to create a directory call nginx-proxy here at the root of the project and put in your ssl cert/key.  See the docs for nginx-proxy.

Once you get the containers fired up, enter the running netmanager container:

sudo docker exec -ti <containerid> bash

And then inside the container:

initialize_netmanager_db development.ini

This will setup the database and create a user N0CALL with a password of pass123.

Add an operator set a password and check the box for a new user.
