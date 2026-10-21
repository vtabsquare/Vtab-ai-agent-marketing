FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MARKETING_DATA_DIR=/data MALLOC_TRIM_THRESHOLD_=65536
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home marketing && mkdir /data && chown marketing:marketing /data
COPY --chown=marketing:marketing app ./app
COPY --chown=marketing:marketing config ./config
COPY --chown=marketing:marketing frontend/dist ./frontend/dist
USER marketing
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:create_app --factory --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --access-log"]
