import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))   # 添加项目根目录到 sys.path，以便导入 config.py

import requests
import json
from config import cfg

from query_stream import client_v1_query
from health_and_version import check_health, check_version
from insert_text import insert_text
from insert_file import insert_file
from query_full import query_full


if __name__ == '__main__':
    # 本地测试时，host需要修改为127.0.0.1
    host_name = "127.0.0.1" if cfg.server.host == "0.0.0.0" else cfg.server.host  
    base_url = f"http://{host_name}:{cfg.server.port}"
    print(f"BASE_URL:{base_url}")
    
    # 1. 检查健康 & 版本
    print('-'*21, "1. 健康检查", '-'*21)
    health_result = check_health(base_url=base_url)
    print("Health check:", health_result)
    version_result = check_version(base_url=base_url)
    print("Version check:", version_result)
    
    # 2. 插入文本检查
    print('-'*21, "2. 文本插入 /insert", '-'*21)
    text = "我的名字叫无师大模型"
    insert_result = insert_text(text, base_url=base_url)
    print("Insert result:", insert_result)
    
    # 3. 插入文件 检查
    # txt 文件
    print('-'*21, "3.1 文件插入-txt /insert_file", '-'*21)
    file_path = 'resources/raw_docs/identity.txt'
    file_result = insert_file(file_path, base_url=base_url)
    print("File insert result:", file_result)
    
    # excel 文件
    print('-'*21, "3.2 文件插入-excel /insert_file", '-'*21)
    file_path = 'resources/raw_docs/identity.xlsx'
    file_result = insert_file(file_path, base_url=base_url)
    print("File insert result:", file_result)
     
    # 4. 整体回复查询
    mode = ["naive","local","global","hybrid", 'mix']
    
    # naive mode
    print('-'*21, "4.1 naive query_full", '-'*21)
    query = "你的名字叫什么"
    print("query:", query)
    temp_mode = mode[0]
    only_need_context = False
    query_result = query_full(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # local mode
    print('-'*21, "4.2 local query_full", '-'*21)
    query = "你是谁"
    print("query:", query)
    temp_mode = mode[1] 
    only_need_context = False
    query_result = query_full(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # global mode
    print('-'*21, "4.3 global query_full", '-'*21)
    query = "你叫啥子"
    print("query:", query)
    temp_mode = mode[2] 
    only_need_context = False
    query_result = query_full(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # hybrid mode
    print('-'*21, "4.4 hybrid query_full", '-'*21)
    query = "怎么称呼你"
    print("query:", query)
    temp_mode = mode[3] 
    only_need_context = False
    query_result = query_full(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # mix mode
    print('-'*21, "4.5 mix query_full", '-'*21)
    query = "我改用什么方式跟你交流"
    print("query:", query)
    temp_mode = mode[4] 
    only_need_context = False
    query_result = query_full(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # 5. 流式查询
    # 5.1 /v1/query 
    print('-'*21, "5.1 流式回复 /v1/query", '-'*21)
    query = "你的组成部份有哪些" 
    print("query:", query)
    client_v1_query(url=f"{base_url}/v1/query", 
                  query=query, 
                  chunksize=1024,
                  um='v1_query_test001',  
                  mode=mode[0], 
                  only_need_context=False)