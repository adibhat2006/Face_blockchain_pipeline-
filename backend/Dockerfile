FROM python:3.10-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install system libraries needed by OpenCV and InsightFace
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirement.txt /app/requirement.txt
RUN pip install --no-cache-dir -r requirement.txt

# Copy backend source code
COPY . /app/

EXPOSE 8000

CMD ["python", "main.py"]
# Use official lightweight Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for OpenCV and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition
COPY requirement.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirement.txt

# Copy backend source code and model weights
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Command to execute backend API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]