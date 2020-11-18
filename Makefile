export PROJECTNAME=$(shell basename "$(PWD)")

.SILENT: ;               # no need for @

setup: ## Setup Virtual Env
	python3 -m venv venv
	./venv/bin/pip3 install -r requirements/dev.txt

deps: ## Install dependencies
	./venv/bin/pip3 install -r requirements/dev.txt

lint: ## Runs black for code formatting
	./venv/bin/black . --exclude venv

clean: ## Clean package
	find . -type d -name '__pycache__' | xargs rm -rf
	rm -rf build dist

deploy: clean ## Copies any changed file to the server
	ssh ${PROJECTNAME} -C 'bash -l -c "mkdir -vp ./${PROJECTNAME}"'
	rsync -avzr \
		.env \
		env.cfg \
		local_main.py \
		app \
		requirements \
		scripts \
		${PROJECTNAME}:./${PROJECTNAME}

data: deploy ## Sets up a screen session on the server and start the app
	ssh ${PROJECTNAME} -C 'bash -l -c "./${PROJECTNAME}/scripts/setup_data_provider.sh"'

strategies: deploy ## Sets up a screen session on the server and start the app
	ssh ${PROJECTNAME} -C 'bash -l -c "./${PROJECTNAME}/scripts/setup_strategy_runner.sh"'

stop: deploy ## Stop any running screen session on the server
	ssh ${PROJECTNAME} -C 'bash -l -c "./${PROJECTNAME}/scripts/stop_strategy_runner.sh"'

ssh: ## SSH into the target VM
	ssh ${PROJECTNAME}

bpython: ## Runs bpython
	./venv/bin/bpython

.PHONY: help
.DEFAULT_GOAL := help

help: Makefile
	echo
	echo " Choose a command run in "$(PROJECTNAME)":"
	echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	echo