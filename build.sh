#!/bin/bash
set -e  # Exit on any failure

IMAGE_NAME="$DOCKER_USERNAME/$APP_NAME"

echo "Building Docker image: $IMAGE_NAME:$IMAGE_TAG"
docker build -t $IMAGE_NAME:$IMAGE_TAG .

echo "Tagging image as latest"
docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:latest

echo "Pushing $IMAGE_TAG and latest to Docker Hub"
docker push $IMAGE_NAME:$IMAGE_TAG
docker push $IMAGE_NAME:latest

echo "Build & push complete: $IMAGE_NAME:$IMAGE_TAG and $IMAGE_NAME:latest"
