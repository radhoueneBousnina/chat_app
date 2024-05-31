# Makefile FOR RUNNING THIS PROJECT ON DOCKER

# the command to use for the Python interpreter
PYTHON=python

# the manage.py script
MANAGE=$(PYTHON) manage.py

DOCKER_COMPOSE=docker-compose
DOCKER_EXEC=$(DOCKER_COMPOSE) exec web
DOCKER_EXEC_MANAGE=$(DOCKER_EXEC) $(MANAGE)


run:
	$(DOCKER_COMPOSE) up --build

app:
	$(DOCKER_EXEC_MANAGE) startapp $(filter-out $@,$(MAKECMDGOALS))

migrations:
	$(DOCKER_EXEC_MANAGE) makemigrations

migrate:
	$(DOCKER_EXEC_MANAGE) migrate

superuser:
	$(DOCKER_EXEC_MANAGE) createsuperuser

test:
	$(DOCKER_EXEC_MANAGE) test

shell:
	$(DOCKER_EXEC_MANAGE) shell

collectstatic:
	$(DOCKER_EXEC_MANAGE) collectstatic --no-input

requirements:
	pip freeze > requirements.txt

install:
	pip install -r requirements.txt


# help
help:
	@echo "Available commands:"
	@echo "  run           : Run the Django development server."
	@echo "  migrations    : Create new migration files based on model changes."
	@echo "  migrate       : Apply database migrations."
	@echo "  superuser     : Create a superuser for the Django project."
	@echo "  test          : Run tests for the Django project."
	@echo "  shell         : Run the Django shell."
	@echo "  collectstatic : Collect static files into the STATIC_ROOT directory."
	@echo "  requirements  : Freeze Python dependencies to requirements.txt."
	@echo "  install       : Install Python dependencies."

.PHONY: help