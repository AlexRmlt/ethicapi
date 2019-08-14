.PHONY: start-dev start-prod logs run-container

TEST_PATH=./
export FLASK_APP=./index.py

help:
	@echo "    start-dev"
	@echo "       Start EthicAPI Flask server (development)"
	@echo "    start-prod"
	@echo "       Start EthicAPI via Heroku (production)"
	@echo "    logs"
	@echo "		  Show application log"	
	@echo "    run-container"
	@echo "       Start EthicAPI server in Docker container"

start-dev:
	flask run -h 0.0.0.0 -p 5000

start-prod:
	heroku local

logs:
	heroku logs --tail

run-container:
	docker run \
		-p 5000:5000 \
		-v $(shell pwd):/app \
		aroemelt/ethicbot:ethicapi \
		gunicorn -w 4 -b 0.0.0.0:5000 index:app