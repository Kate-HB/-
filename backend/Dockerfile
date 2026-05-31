FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_DEBUG=false
CMD gunicorn APP:app -b 0.0.0.0:${PORT:-10000}
