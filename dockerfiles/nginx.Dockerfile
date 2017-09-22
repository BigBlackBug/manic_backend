FROM nginx:latest

MAINTAINER Evgeny Shakhmaev <hello@bigblackbug.me>

ARG profile
ADD ./config/${profile}.nginx.conf /etc/nginx/nginx.conf