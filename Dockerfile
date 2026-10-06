# ============================================================
# STEP 1: PYTHON BASE IMAGE
# ============================================================
FROM python:3.12-slim


# ============================================================
# STEP 2: WORKING DIRECTORY
# ============================================================
WORKDIR /app


# ============================================================
# STEP 3: PYTHON RUNTIME SETTINGS
# ============================================================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# ============================================================
# STEP 4: SYSTEM DEPENDENCIES
# ============================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


# ============================================================
# STEP 5: INSTALL CPU-ONLY PYTORCH
# Required indirectly by:
# BAAI/bge-small-en-v1.5
# -> sentence-transformers
# -> PyTorch
#
# CPU-only because this project does not require CUDA/GPU.
# ============================================================
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch==2.14.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu


# ============================================================
# STEP 6: INSTALL PROJECT DEPENDENCIES
# ============================================================
COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt


# ============================================================
# STEP 7: COPY APPLICATION
# ============================================================
COPY src/ ./src/
COPY docs_dir/ ./docs_dir/
COPY data/ ./data/


# ============================================================
# STEP 8: CREATE LOG DIRECTORY
# ============================================================
RUN mkdir -p /app/logs


# ============================================================
# STEP 9: EXPOSE FASTAPI PORT
# ============================================================
EXPOSE 8000


# ============================================================
# STEP 10: START FASTAPI
# ============================================================
CMD ["uvicorn", "src.backend_src.main:app", "--host", "0.0.0.0", "--port", "8000"]