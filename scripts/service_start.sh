#!/bin/bash

IMAGE_NAME="ssl_checker"
CONTAINER_NAME="ssl_checker_container"
echo "Building image..."
docker build -t $IMAGE_NAME ../
if [ $? -eq 0 ]; then
    OLD_CONTAINER=`docker ps -a |grep $IMAGE_NAME|awk {'print $1'}`
    if [ ! -z "$OLD_CONTAINER" ]; then
        echo "Removing old container $OLD_CONTAINER..."
        docker container rm -f $OLD_CONTAINER
    fi
    echo "Starting container..."
    # Start the container exposing the service on localhost port 5000
    # Prometheus metrics are available at 172.17.0.1:8000
    docker run --name $CONTAINER_NAME -p 5000:5000/tcp -p 172.17.0.1:8000:8000/tcp $IMAGE_NAME
else
    echo "Failed to build image."
    exit 1
fi
