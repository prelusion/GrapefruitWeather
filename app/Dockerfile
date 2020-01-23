FROM python:3.7-alpine

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --dev --system --deploy --ignore-pipfile

ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]