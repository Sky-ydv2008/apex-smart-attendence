FROM python:3.11-slim

# Install system dependencies for OpenCV, EasyOCR, and Node.js for building React
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Build Frontend
COPY frontend /app/frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Set up Backend
WORKDIR /app
COPY backend /app/backend

# Seed initial database
RUN python /app/backend/app/seed.py

ENV PYTHONPATH=/app/backend
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
