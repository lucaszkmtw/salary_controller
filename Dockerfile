FROM python:3.11.0b1-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE 1

RUN apk add --update --no-cache --virtual .tmp-build-deps \
	postgresql-client \
	gcc \
	g++\
	libffi-dev \
	libc-dev \
	linux-headers \
	postgresql-dev \
	curl \
	git \
	ca-certificates

ARG requirements_file
ADD requirements ./requirements

RUN pip install certifi

RUN pip install --upgrade pip & \
	pip install --no-cache-dir \
				-r requirements/${requirements_file} \
				--cert=$(python -c "import certifi; print(certifi.where())")

FROM python:3.11.0b1-alpine AS app

RUN apk --no-cache add postgresql-client git

COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /usr/src/app:$PYTHONPATH
