#!/usr/bin/env bash

if [[ "x${CONTAINER_NAME}" = 'x' ]] ; then
  CONTAINER_NAME="txbitwrap-dev-${1}"
fi

IMAGE_NAME="stackdump/txbitwrap:latest"

docker rm --force $CONTAINER_NAME &>/dev/null

if [[ "x${IMAGE_NAME}" = 'x' ]] ; then
    IMAGE_NAME= "bitwrap/txbitwrap:dev"
    echo "rebuilding: ${IMAGE_NAME}"
    docker build . -t $IMAGE_NAME
fi

# KLUDGE: api must be specified first to listen on http port
if [[ ("x${1}" = 'x') || ("$1" = 'api') ]] ; then
  echo "starting => http://127.0.0.1:8080 worker(s): ${@}"
  docker run -it --name=${CONTAINER_NAME} \
    --link bitwrap-dev:rds \
    --link rabbit-dev:amqp \
    -p 127.0.0.1:8080:8080 \
    ${IMAGE_NAME} $@
else
  echo "starting worker(s): ${@}"
  docker run -it --name=${CONTAINER_NAME} \
    --link bitwrap-dev:rds \
    --link rabbit-dev:amqp \
    ${IMAGE_NAME} $@
fi
