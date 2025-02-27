#!/usr/bin/env python3
import requests
import json
import sys
import argparse

def get_recommendations(songs, api_url="http://localhost:52007/api/recommend"):
    """
    从推荐API获取歌曲推荐
    """
    try:
        # 准备请求
        payload = {"songs": songs}
        headers = {"Content-Type": "application/json"}
        
        # 发送请求
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        
        # 检查响应
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"错误: 服务器返回状态码 {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        print(f"错误: {str(e)}")
        return None

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="播放列表推荐客户端")
    parser.add_argument("--songs", "-s", nargs="+", required=True, help="输入歌曲列表")
    parser.add_argument("--url", "-u", default="http://localhost:52007/api/recommend", help="API URL")
    
    args = parser.parse_args()
    
    # 获取推荐
    result = get_recommendations(args.songs, args.url)
    
    # 打印结果
    if result:
        print("\n推荐歌曲:")
        for i, song in enumerate(result["songs"], 1):
            print(f"{i}. {song}")
        
        print(f"\n模型版本: {result['version']}")
        print(f"模型日期: {result['model_date']}")

if __name__ == "__main__":
    main()