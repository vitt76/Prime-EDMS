# Dockerfile for Video Converter Service
# Based on Ubuntu with FFmpeg for video processing

FROM ubuntu:22.04

# Labels
LABEL maintainer="Converter Pipeline Extension"
LABEL description="Video converter service for Mayan EDMS"
LABEL version="1.0"

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Video processing
    ffmpeg \
    # Audio processing (part of ffmpeg)
    # Image processing for thumbnails
    imagemagick \
    # Python
    python3 \
    python3-pip \
    python3-dev \
    python3-pillow \
    python3-numpy \
    # Utils
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install additional Python packages
RUN pip3 install --no-cache-dir \
    pillow \
    numpy \
    requests

# Create app directory
WORKDIR /app

# Copy converter script
COPY convert_video.py /app/

# Make executable
RUN chmod +x /app/convert_video.py

# Create temp directory
RUN mkdir -p /tmp/converter

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ffmpeg -version > /dev/null && echo "Video converter ready"

# Default command
CMD ["python3", "/app/convert_video.py"]

