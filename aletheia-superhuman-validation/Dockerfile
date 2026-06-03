# Dockerfile: Lean 4 environment for Aletheia proof verification
# Base: Ubuntu 22.04 + Lean 4 (latest stable)

FROM ubuntu:22.04

# Metadata
LABEL maintainer="Aletheia Project"
LABEL description="Lean 4 + Python 3.11 for Erdős problem proof verification"

# Set non-interactive mode + UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core tools
    curl \
    wget \
    git \
    build-essential \
    # Python
    python3.11 \
    python3-pip \
    python3-venv \
    # Lean 4 dependencies
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev \
    # Utilities
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install Lean 4 via elan (Lean version manager)
RUN curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y \
    && . $HOME/.elan/env \
    && lean --version

# Add elan to PATH for all users
ENV PATH="/root/.elan/toolchains/leanprover--lean4---v4.5.0/bin:/root/.elan/bin:${PATH}"

# Verify Lean installation
RUN lean --version

# Create application directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt 2>&1 || true

# Create volume for results
VOLUME ["/app/results"]

# Default command: run Phase C pipeline
CMD ["python3", "scripts/pipeline_phase_c.py"]
