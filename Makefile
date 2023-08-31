VENV_PATH='az-ge/bin/activate'
DOCKER_NAME='ds_great_expectations'
DOCKER_TAG='0.0.3'
AZURE_CONTAINER_REGISTRY='dndsregistry.azurecr.io'

lint:
	black src/

install:
	python3 -m pip install --upgrade pip
	# Used for packaging and publishing
	pip install setuptools wheel twine
	# Used for linting
	pip install black
	# Used for testing
	pip install pytest

env:
	export $$(cat .env | xargs)

build:
	docker build --no-cache -t $(AZURE_CONTAINER_REGISTRY)/$(DOCKER_NAME):$(DOCKER_TAG) .

push:
	docker push $(AZURE_CONTAINER_REGISTRY)/$(DOCKER_NAME):$(DOCKER_TAG)

run:
	docker run -it -p 80:80 --env-file .env $(AZURE_CONTAINER_REGISTRY)/$(DOCKER_NAME):$(DOCKER_TAG)
