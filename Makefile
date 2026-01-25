migrate:
	docker compose run --rm api alembic upgrade head

makemigration:
	docker compose run --rm api alembic revision --autogenerate -m "$(msg)"
