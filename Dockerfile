FROM python:3.6.6-alpine3.8

RUN apk update \
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev \
  && pip install psycopg2==2.7.5 \
  && pip install typed-ast==1.1.0 \
  && apk del build-deps

COPY app/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

EXPOSE 5000

ENV PYTHONPATH /app

CMD ./app

COPY tests /tests
VOLUME /tests

COPY app /app
WORKDIR /app
VOLUME /app

