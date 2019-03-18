FROM python:alpine

LABEL maintainer "Sebastien Durand seb.durand6@gmail.com"

#install postgres client library
RUN apk update && apk add libpq tzdata

RUN cp /usr/share/zoneinfo/Canada/Eastern /etc/localtime
RUN echo "Canada/Eastern" >  /etc/timezone

#install build dependencies
RUN apk add --virtual .build-deps gcc linux-headers musl-dev python3-dev libffi-dev openssl-dev postgresql-dev

#install python packages, including psycopg2-binary
COPY ./requirements.txt /tmp/.
RUN pip install --no-cache-dir -r /tmp/requirements.txt

#clean up build dependencies
RUN apk del .build-deps

# Add a /app volume
VOLUME ["/webapp"]

# Define working directory
WORKDIR /webapp

#run flask server
CMD ["python", "./application.py"]
