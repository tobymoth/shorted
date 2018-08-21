.PHONY: build up down shell psql clean lint.flake8 lint.pylint lint.mypy lint test

EXEC := docker-compose exec shorted

forall_python = \
    $(EXEC) sh -c \
    "find /app /tests -name \*.py | xargs $(1)" 

build:
	docker build --rm -t toby/shorted:1.0 .

up:
	docker-compose up -d

down:
	docker-compose down

shell:
	$(EXEC) sh

psql:
	docker-compose exec postgres /usr/local/bin/psql shorted shorted

clean:
	- docker-compose exec shorted rm -rf /tests/__pycache__

lint.flake8:
	$(call forall_python,flake8)
 
lint.pylint:
	$(call forall_python,pylint --rcfile /app/pylintrc)
 
 lint.mypy:
	$(call forall_python,mypy --ignore-missing-imports --disallow-untyped-defs)

lint: lint.flake8 lint.pylint lint.mypy

test: clean lint.flake8
	$(EXEC) pytest /tests

