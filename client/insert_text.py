import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))   # 添加项目根目录到 sys.path，以便导入 config.py

import requests
import json
from config import cfg

def insert_text(text, base_url):
    """插入文本示例
    
     /insert 接口
    """
    url = f"{base_url}/insert"
    headers = {"Content-Type": "application/json"}
    data = {
        "text": text
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()


if __name__ == '__main__':
    # 本地测试时，host需要修改为127.0.0.1
    host_name = "127.0.0.1" if cfg.server.host == "0.0.0.0" else cfg.server.host  
    base_url = f"http://{host_name}:{cfg.server.port}"
    print(f"BASE_URL:{base_url}")

    
    text = "我的名字叫无师大模型"
    insert_result = insert_text(text, base_url=base_url)
    print("Insert result:", insert_result)