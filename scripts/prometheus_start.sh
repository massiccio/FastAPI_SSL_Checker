#!/bin/bash

OLD_CONTAINER=`(docker ps -a |grep /bin/prometheus|awk {'print $1'})`
if [ ! -z "$OLD_CONTAINER" ]; then
    echo "Removing old container $OLD_CONTAINER"
    docker container rm -f $OLD_CONTAINER
fi
#CUR_DIR=`pwd`
#SCRIPT_PATH=`dirname $0`
# Absolute path to this script. /home/user/bin/foo.sh
SCRIPT=$(readlink -f $0)
# Absolute path this script is in. /home/user/bin
SCRIPT_PATH=`dirname $SCRIPT`
echo $SCRIPT_PATH
docker run --name prometheus -p 9090:9090/tcp -v $SCRIPT_PATH/../conf/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
