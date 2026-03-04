FROM python:3.11

WORKDIR /app

COPY ./app /app

RUN pip install fastapi uvicorn requests psycopg2-binary sqlalchemy

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]