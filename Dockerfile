# This is a simple Dockerfile to use while developing
# It's not suitable for production
#
# Usage: docker run --env-file=.flaskenv image flask run
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code

COPY requirements.txt setup.py tox.ini ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

COPY inventory_api_app inventory_api_app/

EXPOSE 5000
