import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))   # 添加项目根目录到 sys.path，以便导入 config.py

import requests
import json
from config import cfg


def query_full(base_url, query_text, mode="hybrid", only_need_context:bool=False):
    """整体回复查询
    """
    url = f"{base_url}/query/full"
    headers = {"Content-Type": "application/json"}
    data = {
        "query": query_text,
        "mode": mode,
        "only_need_context": only_need_context
    }
    response = requests.post(url, json=data, headers=headers)
    return json.dumps(response.json(), indent=4, ensure_ascii=False)

if __name__ == '__main__':
    # 本地测试时，host需要修改为127.0.0.1
    host_name = "127.0.0.1" if cfg.server.host == "0.0.0.0" else cfg.server.host  
    base_url = f"http://{host_name}:{cfg.server.port}"
    print(f"BASE_URL:{base_url}")
    
    mode = ["naive","local","global","hybrid", "mix"]
    
    # naive mode
    print('-'*21, "1 naive query_full", '-'*21)
    query = "你的名字叫什么"
    print("query:", query)
    temp_mode = mode[0]
    only_need_context = False
    query_result = query_full(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # local mode
    print('-'*21, "2 local query_full", '-'*21)
    query = "你是谁"
    print("query:", query)
    temp_mode = mode[1] 
    only_need_context = False
    query_result = query_full(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # global mode
    print('-'*21, "3 global query_full", '-'*21)
    query = "你叫啥子"
    print("query:", query)
    temp_mode = mode[2] 
    only_need_context = False
    query_result = query_full(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # hybrid mode
    print('-'*21, "4 hybrid query_full", '-'*21)
    query = "怎么称呼你"
    print("query:", query)
    temp_mode = mode[3] 
    only_need_context = False
    query_result = query_full(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # mix mode
    print('-'*21, "5 mix query_full", '-'*21)
    query = "我改用什么方式跟你交流"
    print("query:", query)
    temp_mode = mode[4] 
    only_need_context = False
    query_result = query_full(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])