FROM python:3.10-alpine

ENV BUILD_ONLY_PACKAGES='wget' \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

ENV APP_DIR /app

WORKDIR ${APP_DIR}

RUN apk update \
    && apk add --no-cache --virtual bash \
    git \
    gcc \
    g++ \
    make \
    musl-dev \
    libc-dev \
    linux-headers \
    postgresql-libs \
    postgresql-dev

RUN python -m pip install --upgrade pip

COPY requirements.txt ${APP_DIR}

RUN python -m pip install -r requirements.txt

COPY . ${APP_DIR}

CMD ["python", "main.py"]
