FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["flake8", "--config=.flake8"]