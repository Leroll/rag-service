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

def v1_query_stream_post(url, um, query, 
                         chunksize=1024,  # 接受自服务器的数据块大小
                         mode="naive",
                         only_need_context=False,
                     ):
    request_id = 'test_chat_request_001'
    session_id = 'test_chat_session_001'
    query_mode = "v"
    body = {
        "um": um,
        "request_id": request_id,
        "session_id": session_id,
        "query_mode": query_mode,
        "query": query,
        "mode": mode,
        "only_need_context": only_need_context,
    }
    
    # 创建增量解码器
    decoder = codecs.getincrementaldecoder('utf-8')()
    
    response = requests.post(url, json=body, stream=True)
    
    if response.status_code == 200:
        for chunk in response.iter_content(chunk_size=chunksize):
            if chunk:
                time.sleep(0.1)
                # 使用增量解码器处理字节流
                decoded_chunk = decoder.decode(chunk)
                if decoded_chunk:
                    yield decoded_chunk
        # 处理最后残留的字节
        final_chunk = decoder.decode(b'', final=True)
        if final_chunk:
            yield final_chunk
    else:
        res = f"请求失败\n状态码: {response.status_code}\n响应内容: {response.text}"
        yield res
        
        
def client_v1_query(url, query, um='v1_query_test001', chunksize=1024, mode="naive", only_need_context=False):
    begin = time.perf_counter()
    for i in v1_query_stream_post(url=url, query=query, um=um, 
                                  chunksize=chunksize, mode=mode, 
                                  only_need_context=only_need_context):
        end = time.perf_counter()
        gap = (end - begin)*1000
        begin = end
        print(f"\n------ Recieve Chunk | gap : {gap:.2f}ms  ------")
        print(i)

if __name__ == '__main__':
    # 参数配置
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--query', type=str, 
                        default=None)
    parser.add_argument('-c', '--chunksize', type=int,
                        default=1024)
    args = parser.parse_args()
    
    # 参数落地
    if args.query is None:
        # query = "小明的父亲是谁"
        query = "1"
    else:
        query = args.query  # 修正拼写错误
    chunksize = args.chunksize
    url = f"http://{cfg.server.host}:{cfg.server.port}/v1/query"
    
    # 参数打印
    print('-'*42)
    print('Arguments:')
    print(f"    query: {query}")
    print(f"    chunksize: {chunksize}")
    print(f"    url: {url}")
    print('-'*42)
    
    # 执行
    client_v1_query(url=url, query=query, chunksize=chunksize,
                  um='v1_query_test001',  
                  mode="naive", 
                  only_need_context=False)
    