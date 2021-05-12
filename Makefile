.DEFAULT_GOAL := help
.PHONY: coverage deps help lint publish push test tox

deps: ## install dependencies
	  python -m pip install --upgrade pip
	  python -m pip install -r requirements.txt

ci-deps:
	  python -m pip install black flake8 mccabe pytest tox tox-gh-actions
	  python -m pip install cfn-lint

lint: ##Lint and static check
	  python -m flake8 scripts/
	  cfn-lint cfn/*.yaml
	  python -m black scripts/

black:
	black scripts tests setup.py --check

test:
	python -m pytest -ra

push:  ## push code with targets
	git push && git push --tags

tox: ##Run tox
	python -m tox
	
doc-test: ##mkdocs local test
	python -m pip install mkdocs mkdocstrings
	mkdocs serve

doc-deploy: ##mkdocs github
	python -m pip install mkdocs mkdocstrings
	mkdocs build
	mkdocs gh-deploy

install:
	pip install rich
	python -m pip install -e .

install-dev: install
		python -m pip install -e ".[dev]"
		pre-commit install

install-test: install
		python -m pip install -e ".[test]]"
		python -m pip install -e ".[all]"

clean:
	rm -rf **/.ipynb_checkpoints **/.pytest_cache **/__pycache__ **/**/__pycache__ .ipynb_checkpoints .pytest_cache

help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done
