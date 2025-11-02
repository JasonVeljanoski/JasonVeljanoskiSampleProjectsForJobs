FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

ADD requirements.txt /app/
WORKDIR /app/
RUN pip3 install -r requirements.txt

COPY . /app

ENV PYTHONPATH=/app

EXPOSE 80
