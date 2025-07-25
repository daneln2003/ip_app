#!/bin/bash
set -e  # Exit on any failure

CHART_PATH="helm-chart"
IMAGE_NAME="$DOCKER_USERNAME/$APP_NAME:$IMAGE_TAG"

echo "Deploying $IMAGE_NAME with Helm"
helm upgrade --install "$APP_NAME" "$CHART_PATH" \
  --set image.repository="$DOCKER_USERNAME/$APP_NAME" \
  --set image.tag="$IMAGE_TAG"

echo "Deployment complete"
