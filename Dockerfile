# Python Base Image from https://hub.docker.com/r/arm32v7/python/
FROM arm32v7/python:3.10.5-buster

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
# ENV PYTHONUNBUFFERED 1 <- was in example but don't think I need
COPY . .
CMD python3 main.py
