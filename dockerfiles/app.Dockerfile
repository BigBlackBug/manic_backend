################################
# 4hands2go app Dockerfile
################################

FROM bigblackbug/4hands2go-base:latest

ADD . /code/

# uWSGI will listen on this port
EXPOSE 8000

ENV UWSGI_WSGI_FILE=/code/src/config/wsgi.py UWSGI_HTTP=:8000 \
UWSGI_MASTER=1 UWSGI_WORKERS=2 UWSGI_THREADS=8  \
UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy

# Start uWSGI
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uwsgi", "--http-auto-chunked", "--http-keepalive"]
