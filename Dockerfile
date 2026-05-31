# Stage 1: 构建前端
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Python 后端 + 前端静态文件
FROM python:3.13-slim
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY --from=frontend-build /app/dist ./static

ENV FLASK_DEBUG=false

CMD gunicorn APP:app -b 0.0.0.0:${PORT:-8080}
