SHELL := /bin/bash
PROJECT_NAME = lodge

DOCKER_IMG := $(PROJECT_NAME):latest
DOCKER_RUN := docker run --rm -t

PYTEST := python -B -m pytest -vv -p no:cacheprovider

MOUNT_TEST := -v $(PWD)/test_lodge.py:/lodge/test_lodge.py

# Source https://gist.github.com/coryodaniel/5fb5503953ca799cd51adc6764324780
help: ## Print this beautiful help
	@grep -E '^[a-zA-Z_0-9-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Clean the image
	docker rmi $(DOCKER_IMG) --force

build: ## Build an image to run tests and linter
	docker build -t $(DOCKER_IMG) .

shell: build  ## Opens a shell to interact inside the container
	$(DOCKER_RUN) -i $(DOCKER_IMG) bash

check: build  ## Runs all tests
	$(DOCKER_RUN) $(MOUNT_TEST) $(DOCKER_IMG) $(PYTEST) --cov=$(PROJECT_NAME)

check-interactive: build  ## Runs all tests in interactive mode
	$(DOCKER_RUN) $(MOUNT_TEST) -i $(DOCKER_IMG) $(PYTEST)

check-interactive/%: build  ## Runs all tests in interactive mode
	$(DOCKER_RUN) $(MOUNT_TEST) -i $(DOCKER_IMG) $(PYTEST) $*

lint: build  # Run all static checks
	$(DOCKER_RUN) $(MOUNT_TEST) $(DOCKER_IMG) mypy lodge.py test_lodge.py
	$(DOCKER_RUN) $(MOUNT_TEST) $(DOCKER_IMG) flake8 lodge.py test_lodge.py
