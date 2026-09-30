FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --default-timeout=300 --no-cache-dir -r requirements.txt
COPY app ./app
RUN mkdir -p /app/artifacts
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
