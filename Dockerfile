FROM python:3.10.12-bookworm

ARG VERSION

LABEL org.label-schema.version=$VERSION

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY great_expectations great_expectations

COPY src/api /app/src/api

CMD ["python3", "-m", "src.api"]
