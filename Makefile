.PHONY: dev prod _dev_backend_ _dev_frontend_ activate_prod_env activate_dev_env

MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MAKEFILE_DIR := $(dir $(MAKEFILE_PATH))
LOGGER_DIR := $(MAKEFILE_DIR)parser/logger/

DOCKER_PROJECT_NAME := multi-b2b-api

stop_db:
	docker compose -f ./docker-compose.active.yml stop

run_db: 
	docker compose -p ${DOCKER_PROJECT_NAME} -f ./docker-compose.active.yml up -d

dev: activate_dev_env run_db
	exec npx concurrently -k --graceful-kill 10 "make _dev_backend_" "make _dev_frontend_"

logs:
	@parser_logfile=$$(find "$(LOGGER_DIR)" -name '*.log' | head -n 1); \
	tail --retry -f "$$parser_logfile"

build:
	npm run build

prod: activate_prod_env
	gunicorn parser.main:app \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000

down:
	docker compose -p ${DOCKER_PROJECT_NAME} -f ./docker-compose.active.yml down

remove_db:
	docker compose -p ${DOCKER_PROJECT_NAME} -f ./docker-compose.active.yml down -v

alembic_fresh_migration: stop_db remove_db
# 	Delete versions
	cd parser && rm -rf ./migrations/versions/*
#   Run database
	docker compose -p ${DOCKER_PROJECT_NAME} -f ./docker-compose.active.yml up -d
#   Wait for the database to be ready
	sleep 3
# 	Make revision
	cd parser && ../.venv/bin/python -m alembic revision --autogenerate
#   Upgrade
	cd parser && ../.venv/bin/python -m alembic upgrade heads
#   Stop database
	docker compose -f ./docker-compose.active.yml stop

alembic_migration_version: stop_db
#   Run database
	docker compose -p ${DOCKER_PROJECT_NAME} -f ./docker-compose.active.yml up -d
#   Wait for the database to be ready
	sleep 3
#   Make revision
	cd parser && ../.venv/bin/python -m alembic revision --autogenerate
#   Upgrade
	cd parser && ../.venv/bin/python -m alembic upgrade heads
#   Stop database
	docker compose -f ./docker-compose.active.yml stop

remove_search_db:
	docker volume rm ${DOCKER_PROJECT_NAME}_open_search_data

run_exec_manager: stop_db
#   Run database
	docker compose -p ${DOCKER_PROJECT_NAME} -f ./docker-compose.active.yml up -d
#   Wait for the database to be ready
	sleep 3
#   Run exec_manager .py file
	.venv/bin/python -m parser.core.exec_manager
#   Stop database
	docker compose -f ./docker-compose.active.yml stop

activate_prod_env:
	cp parser/env/.env.prod parser/env/.env.active && cp frontend/src/env/env.prod.js frontend/src/env/env.active.js

activate_dev_env:
	cp parser/env/.env.dev parser/env/.env.active && cp frontend/src/env/env.dev.js frontend/src/env/env.active.js
	cp ./docker-compose.dev.yml ./docker-compose.active.yml

_dev_backend_:
	.venv/bin/python -m uvicorn parser.main:app --reload --reload-dir=parser --host 0.0.0.0 --port 8000

_dev_frontend_:
	npm run dev
