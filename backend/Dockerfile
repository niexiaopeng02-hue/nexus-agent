FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY backend /app
COPY sample_data /sample_data
CMD ["sh", "/app/scripts/start.sh"]
