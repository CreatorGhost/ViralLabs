# YouTube Automation Stack - Full Stack Docker Image
# Builds React frontend + FastAPI backend

# ===== Stage 1: Build Frontend =====
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build the frontend
RUN npm run build

# ===== Stage 2: Production Image =====
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies using uv for faster installs
RUN pip install --upgrade pip uv && uv pip install --system -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY src/ ./src/
COPY main.py ./

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create necessary directories
RUN mkdir -p generated_thumbnails user_data/faces user_data/audio uploads

# Expose port (FastAPI runs on 8001)
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run FastAPI backend (serves both API and frontend)
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"]
