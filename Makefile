up:
	docker compose up -d

down:
	docker compose down

restart: down up

clean:
	docker system prune -a -f

build:
	docker compose build --no-cache

refresh: clean down build up
