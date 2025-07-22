FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    PREFECT_LOGGING_LEVEL=INFO

ARG PREFECT_API_URL
ARG IMAGE_REPO
ARG IMAGE_TAG
ARG WORK_POOL_NAME=my-docker-pool

ENV PREFECT_API_URL=${PREFECT_API_URL} \
    IMAGE_REPO=${IMAGE_REPO} \
    IMAGE_TAG=${IMAGE_TAG} \
    WORK_POOL_NAME=${WORK_POOL_NAME}

CMD ["python", "flow.py"]
