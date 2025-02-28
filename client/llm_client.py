# 23年接口完整复现
import sys
import os 
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

from utils.sseclient import SSEClient
from config import cfg 
from threading import  Thread
import time
import argparse
            
    
def test_chat_stream(url, um, query, 
                     # 下面的参数是纯兼容老参数，没有实际效果
                     max_length=2048, top_p=0.7, temperature=0.95, kdb1=1, kdb2=1, kdb3=1):
    request_id = 'test_chat_request_001'
    session_id = 'test_chat_session_001'
    query_mode = "v"
    body_start = {"um": um, "query_mode": query_mode, "request_id": request_id,
                  "session_id": session_id, "query": query, "max_length": max_length,
                  "top_p": top_p, "temperature": temperature, 
                  "kdb1": kdb1, "kdb2": kdb2, "kdb3": kdb3}
    messages = SSEClient(url, body_start).iter_content()
    for msg in messages:
        a = msg.decode('utf-8', 'ignore')
        b = a.split('\n')
        if (len(b) == 2 and b[-1] != '') or (len(b) == 3 and b[1] != '\r') or (len(b)>3 and b[1] != '\r'):
            c = eval(b[1])
            yield c['answer']


if __name__ == '__main__':
    # 参数配置
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--query', type=str, 
                        default=None)
    args = parser.parse_args()
    
    if args.query is None:
        # query = "小明的父亲是谁"
        query = "1"
    else:
        query = args.query
    print(f"query: {query}", end='\n' + '-'*42 + '\n')
    url = f"http://{cfg.server.host}:{cfg.server.port}" + "/v1/query"
    
    
    # 执行
    for i in test_chat_stream(url=url, um='256', query=query):
        print('[ Recieve Chunk ] :')
        print(i, '\n')
       


