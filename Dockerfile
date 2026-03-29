FROM python:3.11-slim

# Install system dependencies for MediaPipe (OpenGL/GLES)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libegl1-mesa \
    libgles2-mesa \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:10000", "app:app"]
