FROM python:3.11-slim

WORKDIR /app

COPY ../requirements.txt .
COPY ../main.py .
COPY ../config.json .
COPY ../data.json .
COPY ../VERSION .
COPY ../cogs/ ./cogs/
COPY ../utils/ ./utils/
COPY ../scripts/docker-run.sh .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

RUN chmod +x docker-run.sh

CMD ["./docker-run.sh"]