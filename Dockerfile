FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements*.txt ./
ARG INSTALL_PLAYWRIGHT=0
RUN pip install --no-cache-dir -r requirements.txt \
    && if [ "$INSTALL_PLAYWRIGHT" = "1" ]; then \
        pip install --no-cache-dir -r requirements-playwright.txt \
        && python -m playwright install --with-deps chromium; \
    fi
COPY . .
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
