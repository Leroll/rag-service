import sys
import os
import codecs  # 新增导入
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

import requests
from config import cfg 
import argparse
import time
import json

def check_health(base_url):
    """健康检查
    
    /health 接口
    """
    url = f"{base_url}/health"
    response = requests.get(url)
    return response.json()

def check_version(base_url):
    """版本检查
    
    /version 接口
    """
    url = f"{base_url}/version"
    response = requests.get(url)
    return response.json()


if __name__ == "__main__":
    # 本地测试时，host需要修改为127.0.0.1
    host_name = "127.0.0.1" if cfg.server.host == "0.0.0.0" else cfg.server.host  
    base_url = f"http://{host_name}:{cfg.server.port}"
    print(f"BASE_URL:{base_url}")

    health_result = check_health(base_url=base_url)
    print("Health check:", health_result)
    version_result = check_version(base_url=base_url)
    print("Version check:", version_result)