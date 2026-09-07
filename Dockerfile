FROM python:3.11-slim

# Best practices: non-buffering stdout/stderr & prevent .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependency terpisah untuk caching layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY app.py .

# Buat non-root user demi security context AKS
RUN useradd -u 10001 appuser && \
    chown -R appuser:appuser /app

USER 10001

EXPOSE 8080

CMD ["python", "app.py"]