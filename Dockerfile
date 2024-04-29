FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-core.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements-core.txt

COPY . .

ENV DATABASE_URL=sqlite:///odatrade.db \
    JWT_SECRET=odatrade-dev-secret \
    MODE=paper

CMD ["pytest", "tests/", "-q", "--tb=short"]
