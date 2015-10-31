.PHONY: tests server

test:
	python tests.py -v

run: server
server:
	python runserver.py

init-schema:
	dropdb dancar
	createdb dancar
	psql dancar < schema.sql

update-deps:
	pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
