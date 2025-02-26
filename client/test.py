import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))   # 添加项目根目录到 sys.path，以便导入 config.py

import requests
import json
from config import cfg

def check_health(base_url):
    """健康检查
    
    /health 接口
    """
    url = f"{base_url}/health"
    response = requests.get(url)
    return response.json()

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

# 3. 插入文件
def insert_file(file_path, base_url):
    """插入文件示例
    """
    url = f"{base_url}/insert_file"
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files)
    return response.json()


# 4. 查询
def make_query(base_url, query_text, mode="hybrid", only_need_context:bool=False):
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

# 5. 流式查询
# 5.1 新版本流式回复
def test_query_stream(base_url, query_text, mode="hybrid", only_need_context:bool=False):
    """新版本流式回复
    """
    
    # 端点 URL
    url = f"{base_url}/query/stream"  # 请根据实际 host 和 port 修改
    
    # 请求数据
    payload = {
        "query": query_text,
        "mode": mode,
        "only_need_context": only_need_context
    }
    
    # 设置 headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    try:
        # 发送 POST 请求并接收流式响应
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()  # 检查请求是否成功
            
            # 逐行读取流式响应
            for line in response.iter_lines():
                if line:  # 忽略空行
                    decoded_line = line.decode('utf-8')
                    try:
                        # 直接解析 JSON 数据
                        data = json.loads(decoded_line)
                        print(f"Received chunk: {data}")
                    except json.JSONDecodeError:
                        print(f"Raw chunk: {decoded_line}")
                    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# 5.2 老版本流式回复
def test_v1_query(base_url, query_text, mode="hybrid", only_need_context:bool=False):
    """测试 v1/query 接口
    
    累加回复
    """
    # 端点 URL
    url = f"{base_url}/v1/query"  # 请根据实际 host 和 port 修改
    
    # 请求数据（兼容老接口格式）
    payload = {
        "request_id": "test_request_123",
        "session_id": "test_session_123",
        "um": "test_um",
        "query_mode": "v",
        "query": query_text,
        "mode": mode,
        "only_need_context": only_need_context
    }
    
    # 设置 headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    try:
        # 发送 POST 请求并接收流式响应
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()  # 检查请求是否成功
            
            # 逐行读取流式响应
            for line in response.iter_lines():
                if line:  # 忽略空行
                    decoded_line = line.decode('utf-8')
                    try:
                        # 解析 JSON 数据
                        data = json.loads(decoded_line)
                        answer = data.get("answer", "")
                        code = data.get("code", 0)
                        print(f"Received - Code: {code}, Answer: {answer}")
                        
                        # 检查是否结束
                        if code == 201:
                            print("Stream completed")
                            break
                    except json.JSONDecodeError:
                        print(f"Raw chunk: {decoded_line}")
                    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")




if __name__ == '__main__':
    
    # 本地测试时，host需要修改为127.0.0.1
    host_name = "127.0.0.1" if cfg.rag_server.host == "0.0.0.0" else cfg.rag_server.host  
    base_url = f"http://{host_name}:{cfg.rag_server.port}"
    print(f"BASE_URL:{base_url}")
    
    # 1. 检查健康
    print('-'*21, "1. 健康检查", '-'*21)
    health_result = check_health(base_url=base_url)
    print("Health check:", health_result)
    
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
    mode = ["naive","local","global","hybrid"]
    
    # naive mode
    print('-'*21, "4.1 naive query_full", '-'*21)
    query = "你的名字叫什么"
    print("query:", query)
    temp_mode = mode[0]
    only_need_context = False
    query_result = make_query(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # local mode
    print('-'*21, "4.2 local query_full", '-'*21)
    query = "你是谁"
    print("query:", query)
    temp_mode = mode[1] 
    only_need_context = False
    query_result = make_query(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # global mode
    print('-'*21, "4.3 global query_full", '-'*21)
    query = "你叫啥子"
    print("query:", query)
    temp_mode = mode[2] 
    only_need_context = False
    query_result = make_query(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # hybrid mode
    print('-'*21, "4.4 hybrid query_full", '-'*21)
    query = "怎么称呼你"
    print("query:", query)
    temp_mode = mode[3] 
    only_need_context = False
    query_result = make_query(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    print(f"Query result [{temp_mode}]:", query_result)
    print(json.loads(query_result)['data'])
    
    # 5. 流式查询
    mode = ["naive","local","global","hybrid"]
    
    # 5.1 /query/stream 
    print('-'*21, "5.1 流式回复 /query/stream", '-'*21)
    query = "你有哪些模块"
    print("query:", query)
    temp_mode = mode[0] 
    only_need_context = False
    test_query_stream(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)
    
    # 5.2 /v1/query 
    print('-'*21, "5.2 流式回复 /v1/query", '-'*21)
    query = "你的组成部份有哪些" 
    print("query:", query)
    temp_mode = mode[0] 
    only_need_context = False 
    test_query_stream(base_url=base_url, query_text=query, mode=temp_mode, only_need_context=only_need_context)