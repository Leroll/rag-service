import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))   # 添加项目根目录到 sys.path，以便导入 config.py

import requests
import json
from config import cfg
import time

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
    dir_path = cfg.scene.path + '/raw_docs'
    
    
    # 获取file_paths
    file_paths = []
    for f in os.listdir(dir_path):  
        file_path = dir_path + '/' + f
        if os.path.isfile(file_path):
            file_paths.append(file_path)
    
    # # 本地测试时，可以手动指定file_paths
    # file_paths = [
    #     'resources/raw_docs/identity.txt',
    #     'resources/raw_docs/identity.xlsx',
    #     # 'resources/raw_企业分析报告/附件-2.doc',
    # ]
    
    
    print("File paths:", file_paths)
    for path in file_paths:
        t0 = time.perf_counter()
        print('-'*21, "文件插入", '-'*21)
        print("File path:", path)
        file_result = insert_file(path, base_url=base_url)
        print("File insert result:", file_result)
        t1 = time.perf_counter()
        print(f"Time cost: {t1-t0:.3f}s")