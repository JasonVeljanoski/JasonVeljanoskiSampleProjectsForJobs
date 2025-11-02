FROM python:3.11

RUN apt update
RUN apt install poppler-utils -y

ADD requirements.txt /app/
COPY . /app
WORKDIR /app/

RUN pip3 install -r requirements.txt
RUN pip3 install uvicorn websockets

ENV PYTHONPATH=/app

EXPOSE 80