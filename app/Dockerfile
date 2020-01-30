FROM python:3.7-alpine

RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

WORKDIR /app
COPY . /app

ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]
EXPOSE 5000
