

# ----------- Configuration Variables -----------
IMAGE_NAME=edabot
REGION = eu-central-1
ECR_REPO = 169158972420.dkr.ecr.eu-central-1.amazonaws.com/edabot/edabot
TAG = latest
PORT = 8000



# Build Docker Image
build:
	docker build -t $(IMAGE_NAME) .


# Login to ECR
ecr_login:
	aws ecr get-login-password --region $(REGION) | docker login --username AWS --password-stdin $(ECR_REPO)

# Tag Docker image for ECR
tag:
	docker tag $(IMAGE_NAME) $(ECR_REPO):$(TAG)

# Push to ECR
push: tag
	docker push $(ECR_REPO):$(TAG)

# Build, login, tag, and push in one go
deploy: build ecr_login push

# Makefile for building and pushing Docker image to AWS ECR

# ----------- Configuration Variables -----------
IMAGE_NAME=edabot
REGION = eu-central-1
ECR_REPO = 169158972420.dkr.ecr.eu-central-1.amazonaws.com/edabot/edabot
TAG = latest
PORT = 8000



# Build Docker Image
build:
	docker build -t $(IMAGE_NAME) .


# Login to ECR
ecr_login:
	aws ecr get-login-password --region $(REGION) | docker login --username AWS --password-stdin $(ECR_REPO)

# Tag Docker image for ECR
tag:
	docker tag $(IMAGE_NAME) $(ECR_REPO):$(TAG)

# Push to ECR
push: tag
	docker push $(ECR_REPO):$(TAG)

# Build, login, tag, and push in one go
deploy: build ecr_login push
