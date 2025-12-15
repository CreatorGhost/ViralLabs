# syntax=docker/dockerfile:1.4
# YouTube Automation Stack - Full Stack Docker Image
# Builds React frontend + FastAPI backend

# ===== Stage 1: Build Frontend =====
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies with cache
RUN --mount=type=cache,target=/root/.npm npm ci

# Copy frontend source
COPY frontend/ ./

# Build the frontend
RUN npm run build

# ===== Stage 2: Production Image =====
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies with apt cache for faster rebuilds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with pip cache
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/uv \
    pip install --upgrade pip uv && uv pip install --system -r requirements.txt && uv pip install --system psycopg2-binary

# Copy application code
COPY backend/ ./backend/
COPY src/ ./src/
COPY scripts/ ./scripts/

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create necessary directories and make startup script executable
RUN mkdir -p generated_thumbnails user_data/faces user_data/audio uploads && \
    chmod +x scripts/start.sh

# Expose port (FastAPI runs on 8001)
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run startup script (handles migrations intelligently)
CMD ["./scripts/start.sh"]
