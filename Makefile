.PHONY: init build run db-migrate db-upgrade test tox lint

init: build run
	docker-compose exec web inventory_api_app db upgrade
	docker-compose exec web inventory_api_app init
	@echo "Init done, containers running"

build:
	docker-compose build

run:
	docker-compose up -d

db-migrate:
	docker-compose exec web inventory_api_app db migrate

db-upgrade:
	docker-compose exec web inventory_api_app db upgrade

test:
	docker-compose run -v $(PWD)/tests:/code/tests:ro web tox -e test

tox:
	docker-compose run -v $(PWD)/tests:/code/tests:ro web tox -e py312

lint:
	docker-compose run web tox -e lint
