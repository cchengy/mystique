FROM node:22.14.0-alpine3.21 AS web-build
WORKDIR /build/web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.13.7-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SERVIDOR_HOST=0.0.0.0 \
    SERVIDOR_PORTA=8000 \
    MYSTIQUE_WEB_DIST=/app/web/dist
WORKDIR /app
RUN groupadd --system mystique && useradd --system --gid mystique --home-dir /app mystique
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=mystique:mystique . ./
COPY --from=web-build --chown=mystique:mystique /build/web/dist ./web/dist
USER mystique
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/config', timeout=3)"]
CMD ["python", "-m", "servidor"]
