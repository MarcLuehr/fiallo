#!/bin/sh
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
DOCKERUSER=dockeruser
touch $XAUTH
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -
mkdir -p $HOME/docker/pyqt5

docker run -d --net host --name pyqt5 \
        --volume=$XSOCK:$XSOCK:rw \
        --volume=$XAUTH:$XAUTH:rw \
        --volume=$HOME/docker/pyqt5:/home/$DOCKERUSER/workbench:rw \
        --env="XAUTHORITY=${XAUTH}" \
        --env="DISPLAY" \
        --user="$DOCKERUSER" \
    local/pyqt5
