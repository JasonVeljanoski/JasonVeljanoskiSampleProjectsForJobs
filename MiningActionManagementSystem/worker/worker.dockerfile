FROM ubuntu:20.04

RUN apt-get update && apt-get install -y cron && apt-get -y install curl

COPY tasks /etc/cron.d/tasks

ARG API_KEY
RUN echo "API_KEY=${API_KEY}" >> /etc/environment

RUN chmod 0644 /etc/cron.d/tasks && crontab /etc/cron.d/tasks
