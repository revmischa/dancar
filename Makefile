.PHONY: tests server

test:
	python tests.py

run: server
server:
	python runserver.py

init-schema:
	dropdb dancar
	createdb dancar
	psql dancar < schema.sql
