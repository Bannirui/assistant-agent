FROM python:3.12-slim

# 从docker-compose读环境变量
ARG HTTP_PROXY
ARG HTTPS_PROXY

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

EXPOSE 8000

# 启动服务
CMD ["python", "-m", "src"]
