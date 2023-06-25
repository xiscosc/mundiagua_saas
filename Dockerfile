FROM python:3.10-alpine

WORKDIR /app
COPY . .
RUN apk add --no-cache libcurl build-base curl-dev postgresql-libs gcc musl-dev postgresql-dev libffi-dev
ENV PYCURL_SSL_LIBRARY=openssl
ENV DJANGO_SETTINGS_MODULE=mundiagua_python.settings_app
RUN pip3 install -r requirements.txt
EXPOSE 8080
CMD ["gunicorn", "--worker-tmp-dir", "/dev/shm", "--config", "gunicorn_config.py", "mundiagua_python.wsgi:application"]