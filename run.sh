#!/usr/bin/env bash

if [[ "${1}x" = 'x' ]] ; then
  CONTAINER_NAME='txbitwrap-dev'
else
  CONTAINER_NAME=$1
fi
echo "rebuilding: ${CONTAINER_NAME}"

docker rm --force $CONTAINER_NAME &>/dev/null
docker build . -t bitwrap/txbitwrap:dev

docker run -it --name=${CONTAINER_NAME} \
  --link bitwrap-dev:rds \
  -v ${HOME}:/opt/bitwrap \
  -p 127.0.0.1:8080:8080 \
  bitwrap/txbitwrap:dev
