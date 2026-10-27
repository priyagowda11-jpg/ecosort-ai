
FROM python:3.11-slim

WORKDIR /srv

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY ml/artifacts ./artifacts

ENV ART_DIR=/srv/artifacts
ENV DATABASE_URL=sqlite:////tmp/ecosort.db

EXPOSE 10000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
