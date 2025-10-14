# Dockerfile for RAW Image Converter Service
# Based on Ubuntu with dcraw and libraw for RAW image processing

FROM ubuntu:22.04

# Labels
LABEL maintainer="Converter Pipeline Extension"
LABEL description="RAW image converter service for Mayan EDMS"
LABEL version="1.0"

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # RAW processing tools
    dcraw \
    libraw-bin \
    libraw-dev \
    liblcms2-dev \
    libgomp1 \
    # Image processing
    imagemagick \
    # Python and dependencies
    python3 \
    python3-pip \
    python3-dev \
    python3-numpy \
    python3-pillow \
    # Utils
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for RAW processing
RUN pip3 install --no-cache-dir \
    rawpy \
    imageio \
    numpy \
    pillow

# Create app directory
WORKDIR /app

# Copy converter script
COPY convert_raw.py /app/

# Make executable
RUN chmod +x /app/convert_raw.py

# Create temp directory
RUN mkdir -p /tmp/converter

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import rawpy; print('RAW converter ready')"

# Default command
CMD ["python3", "/app/convert_raw.py"]

