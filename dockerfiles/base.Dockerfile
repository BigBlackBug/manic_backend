################################
# 4hands2go app base Dockerfile
################################

FROM python:3.6

MAINTAINER Evgeny Shakhmaev <hello@bigblackbug.me>

RUN apt-get update && \
    apt-get install -y postgresql postgresql-client && \
    pip3 install uwsgi

RUN \
    groupadd code_executor_group && \
    useradd code_executor_user -g code_executor_group -u 1000

RUN mkdir /code/ && chown -R code_executor_user:code_executor_group /code

WORKDIR /code/

ADD ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt
