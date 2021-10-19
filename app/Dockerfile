#Based on example from here https://hub.docker.com/_/python

FROM python:3.10-slim-buster

EXPOSE 8000

WORKDIR /src

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .

CMD uvicorn main:app --host=0.0.0.0 --reload
