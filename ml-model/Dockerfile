FROM python:3.9-slim

WORKDIR /app

# 复制需要的文件
COPY model_generator.py /app/
COPY requirements.txt /app/

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量默认值
ENV INPUT_DATASET=/data/spotify_dataset.csv
ENV OUTPUT_MODEL=/mnt/model/playlist_rules.pkl
ENV OUTPUT_METADATA=/mnt/model/metadata.txt

# 运行模型生成器
CMD ["python", "model_generator.py"]