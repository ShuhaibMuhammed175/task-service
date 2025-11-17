FROM python:3.11-slim

WORKDIR /app

# Install PostgreSQL development libraries for psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

#CMD ["sh", "-c", "python wait_for_db.py && python manage.py runserver 0.0.0.0:8000"]
CMD ["sh", "-c", "python wait_for_db.py && python manage.py runserver 0.0.0.0:8001"]

