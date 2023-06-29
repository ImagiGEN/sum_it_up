COMPOSE_BASE := docker-compose

init-venv:
	python3 -m venv .venv

pytest:
	pytest -v fastapi;

build-up:
	$(COMPOSE_BASE)	-f docker-compose-local.yml up -d --build;

up:	
	$(COMPOSE_BASE)	-f docker-compose-local.yml up -d;

restart:	
	$(COMPOSE_BASE)	-f docker-compose-local.yml restart;

down:
	$(COMPOSE_BASE)	-f docker-compose-local.yml down;
