FROM python:3.10.13-slim-bullseye

WORKDIR /app

# --- ADD THIS BLOCK ---
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir setuptools wheel
# ----------------------

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "laydies_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
