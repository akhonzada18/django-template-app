FROM python:3.10-slim as base

# Make Playwright installs deterministic & cache-agnostic
# (browsers live in site-packages instead of ~/.cache)
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
    # PLAYWRIGHT_BROWSERS_PATH=0 \
    
# Working directory inside the container
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-openbsd \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt . 

RUN apt-get update

RUN pip install -r requirements.txt
COPY . .

# (optional) build-time collectstatic
RUN python3 manage.py collectstatic --verbosity 3 --noinput

# Uncomment to enable the entrypoint script (waits for DB, runs migrations):
# RUN chmod +x /app/entrypoint.sh
# ENTRYPOINT [ "/app/entrypoint.sh" ]
