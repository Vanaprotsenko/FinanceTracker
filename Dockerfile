FROM python:3.10-slim

WORKDIR /code

COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/code

COPY . /code

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]