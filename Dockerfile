FROM python:3.8

WORKDIR /home

ENV TELEGRAM_API_TOKEN=""
ENV TELEGRAM_ACCESS_ID=""
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir db
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && apt-get update && apt-get install sqlite3
COPY *.py ./
COPY createdb.sql ./
COPY config.json ./

ENTRYPOINT ["python", "server.py"]

