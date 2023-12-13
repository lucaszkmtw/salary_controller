FROM jupyter/scipy-notebook

ENV http_proxy=http://proxy.ips.gba.gov.ar:80
ENV https_proxy=http://proxy.ips.gba.gov.ar:80

WORKDIR /home/jovyan/app
COPY requirements.txt .


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN pip install -r requirements.txt
RUN pip install django-extensions==3.1.3

WORKDIR /home/jovyan/work
