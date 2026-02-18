    FROM python:3.11-slim

    WORKDIR /code

    RUN apt-get update \
        && apt-get install -y --no-install-recommends postgresql-client \
        && rm -rf /var/lib/apt/lists/*

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PYTHONPATH=/code

    COPY . .

    COPY scripts/run_migrations.sh /run_migrations.sh
    RUN chmod +x /run_migrations.sh

    ENTRYPOINT ["/run_migrations.sh"]

    CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
