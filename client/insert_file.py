import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))   # 添加项目根目录到 sys.path，以便导入 config.py

import requests
import json
from config import cfg

def insert_file(file_path, base_url):
    """插入文件示例
    """
    url = f"{base_url}/insert_file"
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files)
    return response.json()


if __name__ == '__main__':
    # 本地测试时，host需要修改为127.0.0.1
    host_name = "127.0.0.1" if cfg.server.host == "0.0.0.0" else cfg.server.host  
    base_url = f"http://{host_name}:{cfg.server.port}"
    print(f"BASE_URL:{base_url}")
    
    # txt 文件
    print('-'*21, "文件插入-txt /insert_file", '-'*21)
    file_path = 'resources/raw_docs/identity.txt'
    file_result = insert_file(file_path, base_url=base_url)
    print("File insert result:", file_result)
    
    # excel 文件
    print('-'*21, "文件插入-excel /insert_file", '-'*21)
    file_path = 'resources/raw_docs/identity.xlsx'
    file_result = insert_file(file_path, base_url=base_url)
    print("File insert result:", file_result)