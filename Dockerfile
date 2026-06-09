# Python 3.8: current runpod SDKs require >=3.8. (Python 3.7 is stuck on the
# ancient runpod 0.9.9, whose work_loop crashes on RunPod's current job format
# with KeyError: 'input'.) All other pinned deps below are 3.8-compatible.
FROM python:3.8-slim

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies required by scipy/numpy/sklearn
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    libgl1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install PyTorch CPU (compatible with Python 3.8)
RUN pip install torch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cpu

# Install pip packages
RUN pip install --upgrade pip && \
    pip install \
        numpy==1.18.5 \
        scipy==1.7.3 \
        pandas==1.3.5 \
        scikit-learn==1.0.2 \
        tqdm

# Install trimesh + deps
RUN pip install \
        trimesh==3.9.29 \
        networkx==2.5 \
        shapely \
        pyglet

# -------------------------------------------------------
# Install SMPL-X
# -------------------------------------------------------
RUN pip install smplx==0.1.28

# Install plotly
RUN pip install plotly==5.3.1

# RunPod serverless SDK — PIN it so a rebuild can't silently pull an
# incompatible version again. 1.7.13 is a current, stable line (needs >=3.8).
RUN pip install "runpod==1.7.13"

# -------------------------------
# Copy the entire project
# -------------------------------
COPY SMPL-Anthropometry /workspace/SMPL-Anthropometry

# Set working directory
WORKDIR /workspace/SMPL-Anthropometry

# -------------------------------
# Start serverless handler
# -------------------------------
CMD ["python", "-u", "runpod_handler.py"]