from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os
import time
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)
# 配置
MODEL_PATH = os.environ.get('MODEL_PATH', '/mnt/model/playlist_rules.pkl')
METADATA_PATH = os.environ.get('METADATA_PATH', '/mnt/model/metadata.txt')
VERSION = os.environ.get('VERSION', '1.0.0')

# 缓存变量
model = None
model_metadata = {}
last_model_check = 0
model_last_modified = 0

def load_model_metadata():
    """加载模型元数据"""
    global model_metadata
    
    if os.path.exists(METADATA_PATH):
        metadata = {}
        with open(METADATA_PATH, 'r') as f:
            for line in f:
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    metadata[key.strip()] = value.strip()
        model_metadata = metadata
        return metadata
    return {}

def load_model():
    """加载模型并返回"""
    global model, model_last_modified
    
    if os.path.exists(MODEL_PATH):
        modified_time = os.path.getmtime(MODEL_PATH)
        with open(MODEL_PATH, 'rb') as f:
            model_data = pickle.load(f)
        model_last_modified = modified_time
        load_model_metadata()
        return model_data
    return None

def check_model_update():
    """检查模型是否有更新，如果有则重新加载"""
    global model, last_model_check, model_last_modified
    
    current_time = time.time()
    # 每60秒检查一次更新
    if current_time - last_model_check > 60:
        if os.path.exists(MODEL_PATH):
            modified_time = os.path.getmtime(MODEL_PATH)
            if modified_time > model_last_modified:
                app.logger.info("检测到模型更新，正在重新加载...")
                model = load_model()
                app.logger.info("模型重新加载完成")
        last_model_check = current_time

def get_recommendations(input_songs, max_recommendations=10):
    """基于输入歌曲列表生成推荐"""
    global model
    
    # 确保模型已加载
    if model is None:
        model = load_model()
        if model is None:
            return []
    
    # 检查模型更新
    check_model_update()
    
    recommendations = {}
    
    # 对于每首输入歌曲，获取推荐并给它们打分
    for song in input_songs:
        if song in model['recommendations']:
            for rec_song, count in model['recommendations'][song]:
                # 不推荐已经在输入中的歌曲
                if rec_song not in input_songs:
                    if rec_song not in recommendations:
                        recommendations[rec_song] = 0
                    recommendations[rec_song] += count
    
    # 按分数排序推荐
    sorted_recommendations = sorted(
        [(song, score) for song, score in recommendations.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    # 返回前N首推荐歌曲
    return [song for song, _ in sorted_recommendations[:max_recommendations]]

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """处理推荐请求的API端点"""
    try:
        data = request.get_json(force=True)
        
        # 验证输入
        if 'songs' not in data or not isinstance(data['songs'], list):
            return jsonify({
                'error': '请求必须包含歌曲列表',
                'version': VERSION
            }), 400
        
        songs = data['songs']
        
        # 获取推荐
        recommendations = get_recommendations(songs)
        
        # 获取模型日期
        model_date = model_metadata.get('model_date', 'unknown')
        
        # 返回推荐结果
        return jsonify({
            'songs': recommendations,
            'version': VERSION,
            'model_date': model_date
        })
        
    except Exception as e:
        app.logger.error(f"处理请求时发生错误: {str(e)}")
        return jsonify({
            'error': f'处理请求时发生错误: {str(e)}',
            'version': VERSION
        }), 500

if __name__ == '__main__':
    # 加载模型
    if model is None:
        model = load_model()
        load_model_metadata()
        if model is None:
            app.logger.warning(f"无法加载模型，将在请求时重试: {MODEL_PATH}")
    
    # 获取端口号
    port = int(os.environ.get('PORT', 5000))
    
    # 启动服务器
    app.run(host='0.0.0.0', port=port)