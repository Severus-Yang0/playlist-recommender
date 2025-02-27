FROM python:3.9-slim

WORKDIR /app

# 复制需要的文件
COPY app.py /app/
COPY requirements.txt /app/

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量默认值
ENV MODEL_PATH=/mnt/model/playlist_rules.pkl
ENV METADATA_PATH=/mnt/model/metadata.txt
ENV PORT=5000
ENV VERSION=1.0.0

# 暴露端口
EXPOSE 5000

# 运行Flask应用
CMD gunicorn --bind 0.0.0.0:${PORT} app:app