# Start from official, minimal Linux image with Python 3.14
FROM python:3.14-slim

# PYTHONDONTWRITEBYTECODE: skips writing .pyc files
# PYTHONUNBUFFERED: makes logs appear immediately instead of being held back
ENV PYTHONDONTWRITEBYTECODE=1 \ 
    PYTHONUNBUFFERED=1

# Folder inside container where code will live
WORKDIR /app

# Copy requirements.txt first so dependencies are only reinstalled when it changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Gathers static files while building image. Settings require SECRET_KEY to load. 
RUN SECRET_KEY=build-only-not-secret python manage.py collectstatic --noinput

EXPOSE 8000

# Runs on container start. Applies database migrations and starts gunicorn
# --workers 2 runs two separate processes, so if one crashes the other keeps serving
# --threads 4 gives each worker 4 threads, so it can handle several connections at once.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 --timeout 120"]