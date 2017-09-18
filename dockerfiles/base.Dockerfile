################################
# 4hands2go app base Dockerfile
################################

FROM python:3.6

MAINTAINER Evgeny Shakhmaev <hello@bigblackbug.me>

RUN apt-get update && \
    apt-get install -y && \
    pip3 install uwsgi

RUN mkdir /code/
WORKDIR /code/

ADD ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt
