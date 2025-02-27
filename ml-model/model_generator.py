import pandas as pd
import numpy as np
import pickle
import os
import time
from datetime import datetime
from collections import defaultdict

# 配置路径
INPUT_DATASET = os.environ.get('INPUT_DATASET', '/home/datasets/spotify/2023_spotify_ds1.csv')
OUTPUT_MODEL = os.environ.get('OUTPUT_MODEL', '/mnt/model/playlist_rules.pkl')
OUTPUT_METADATA = os.environ.get('OUTPUT_METADATA', '/mnt/model/metadata.txt')

print(f"使用数据集: {INPUT_DATASET}")
print(f"模型将保存到: {OUTPUT_MODEL}")

# 创建输出目录
os.makedirs(os.path.dirname(OUTPUT_MODEL), exist_ok=True)

# 初始化共现矩阵（使用嵌套字典来节省内存）
song_cooccurrence = defaultdict(lambda: defaultdict(int))
song_counts = defaultdict(int)
playlist_count = 0

# 分块读取数据集并更新共现矩阵
print("正在读取数据集并构建共现矩阵...")
start_time = time.time()

# 按播放列表ID分组处理数据
chunk_size = 100000  # 每次处理10万行
current_pid = None
current_songs = []

for chunk in pd.read_csv(INPUT_DATASET, chunksize=chunk_size):
    for _, row in chunk.iterrows():
        pid = row['pid']
        song = row['track_name']
        
        # 如果是新的播放列表
        if pid != current_pid:
            # 处理上一个播放列表的共现关系
            if current_songs:
                playlist_count += 1
                # 更新每首歌的计数
                for song in current_songs:
                    song_counts[song] += 1
                
                # 更新共现矩阵
                for i, song1 in enumerate(current_songs):
                    for song2 in current_songs[i+1:]:
                        song_cooccurrence[song1][song2] += 1
                        song_cooccurrence[song2][song1] += 1
            
            # 重置为新的播放列表
            current_pid = pid
            current_songs = [song]
        else:
            # 继续当前播放列表
            current_songs.append(song)

# 处理最后一个播放列表
if current_songs:
    playlist_count += 1
    for song in current_songs:
        song_counts[song] += 1
    
    for i, song1 in enumerate(current_songs):
        for song2 in current_songs[i+1:]:
            song_cooccurrence[song1][song2] += 1
            song_cooccurrence[song2][song1] += 1

print(f"数据处理完成，共 {playlist_count} 个播放列表，{len(song_counts)} 首歌曲，耗时 {time.time() - start_time:.2f} 秒")

# 生成推荐规则
print("正在生成推荐规则...")
start_time = time.time()

# 为每首歌创建推荐列表（基于共现频率）
recommendation_rules = {}
for song in song_counts:
    # 获取所有共现歌曲
    cooccurrences = song_cooccurrence[song]
    
    # 按共现次数排序
    sorted_recommendations = sorted(
        [(other_song, count) for other_song, count in cooccurrences.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    # 存储前20个推荐
    recommendation_rules[song] = sorted_recommendations[:20]

print(f"规则生成完成，共 {len(recommendation_rules)} 首歌曲的推荐规则，耗时 {time.time() - start_time:.2f} 秒")

# 保存规则
print("正在保存模型...")
model_data = {
    'recommendations': recommendation_rules,
    'song_counts': song_counts
}

with open(OUTPUT_MODEL, 'wb') as f:
    pickle.dump(model_data, f)

# 保存元数据
metadata = {
    'model_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'dataset': INPUT_DATASET,
    'num_playlists': playlist_count,
    'num_songs': len(song_counts),
    'num_recommendation_rules': len(recommendation_rules)
}

with open(OUTPUT_METADATA, 'w') as f:
    for key, value in metadata.items():
        f.write(f"{key}: {value}\n")

print("模型生成与保存完成！")
print(f"为 {len(recommendation_rules)} 首歌曲生成了推荐规则，基于 {playlist_count} 个播放列表")
print(f"模型保存在 {OUTPUT_MODEL}")
print(f"元数据保存在 {OUTPUT_METADATA}")