# 23年接口完整复现
import sys
import os 
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

from utils.sseclient import SSEClient
from config import cfg 
from threading import  Thread
import time

url = f"http://{cfg.rag_server.host}:{cfg.rag_server.port}" + "/v1/query"

def top_texts_postprocess(top_list):
    return "***** \n".join(top_list)


def gui_chat_stream(session_id, query, max_length, top_p, temperature, kdb1=1, kdb2=1, kdb3=1):
    um = 'gui_demo_um_001'
    request_id = 'gui_demo_request_001'
    session_id = session_id
    query_mode = "v"
    body_start = {"um": um, "query_mode": query_mode, "request_id": request_id,
                  "session_id": session_id, "query": query, "max_length": max_length,
                  "top_p": top_p, "temperature": temperature, 
                  "kdb1": kdb1, "kdb2": kdb2, "kdb3": kdb3}
    print(body_start)
    messages = SSEClient(url, body_start).iter_content()
    for msg in messages:
        a = msg.decode('utf-8', 'ignore')
        b = a.split('\n')
        if (len(b) == 2 and b[-1] != '') or (len(b) == 3 and b[1] != '\r') or (len(b)>3 and b[1] != '\r'):
            c = eval(b[1])
            print(c['answer'])
            yield c['answer']
            
    
def test_chat_stream(um, query, max_length, top_p, temperature, kdb1=1, kdb2=1, kdb3=1):
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
    
    



def single(text, a):
    for i in test_chat_stream(a, text, 2048, 0.7, 0.95, 1, 1, 1):
        r = i 





if __name__ == '__main__':
    # query = "小明的父亲是谁"
    query = "1"
    print(query, end='-'*42+'\n')
    
    for i in test_chat_stream('256', query, 2048, 0.7, 0.95, 1, 1, 1):
        print(i, '\n')
        print('***')


