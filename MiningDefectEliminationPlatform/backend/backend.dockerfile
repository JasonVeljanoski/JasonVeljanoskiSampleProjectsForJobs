FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ADD requirements.txt /app/
WORKDIR /app/
RUN pip3 install -r requirements.txt

# Dependencied break from Mac -> Linux
RUN pip3 install docxtpl

# Install the latest version of LibreOffice
RUN apt update && apt install -y libreoffice

COPY . /app

ENV PYTHONPATH=/app

EXPOSE 80
