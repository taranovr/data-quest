#!/bin/bash

export AWS_DEFAULT_REGION="us-east-1"

# Define variables
IMAGE_NAME="data-quest"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
ECR_REPO_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_NAME:latest"

docker logout public.ecr.aws
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com

# Build Docker image, Create ECR repo and deploy image
# Check if the ECR repository exists
if aws ecr describe-repositories --repository-names $IMAGE_NAME &>/dev/null; then
    echo "Deleting existing ECR repository..."
    aws ecr delete-repository --repository-name $IMAGE_NAME --force
fi

if docker image inspect "$IMAGE_NAME" &>/dev/null; then
    docker rmi "$IMAGE_NAME"
    echo "Image $IMAGE_NAME deleted successfully."
fi

if docker image inspect "$ECR_REPO_URL" &>/dev/null; then
    docker rmi "$ECR_REPO_URL"
    echo "Image $ECR_REPO_URL deleted successfully."
fi

aws ecr create-repository --repository-name $IMAGE_NAME --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
docker build --platform linux/amd64 -t $IMAGE_NAME:latest .
docker tag $IMAGE_NAME:latest $ECR_REPO_URL
docker push $ECR_REPO_URL
