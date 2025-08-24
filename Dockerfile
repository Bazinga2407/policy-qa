# Multi-stage build for React frontend and Python backend

# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-build
WORKDIR /frontend

# Accept build args for React environment variables
ARG REACT_APP_API_KEY
ENV REACT_APP_API_KEY=$REACT_APP_API_KEY

COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend with served frontend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for document parsing
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app ./app
COPY ./data ./data
COPY ./evals ./evals

# Copy built React frontend
COPY --from=frontend-build /frontend/build ./frontend/build

# Create storage directory
RUN mkdir -p /app/storage

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]