#!/bin/sh
docker stop $1
docker rm $1
docker rmi flood-image:1.0
docker build -t flood-image:1.0 .
docker run -d -p 8003:8501 --network mongo-network --name flood-ctnr flood-image:1.0