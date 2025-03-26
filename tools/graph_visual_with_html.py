"""
基于当前cofig中配置的rag库，生成对应知识图谱的html文件
"""

import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 添加项目根目录到 sys.path，以便导入 config.py

import pipmaster as pm

if not pm.is_installed("pyvis"):
    pm.install("pyvis")
if not pm.is_installed("networkx"):
    pm.install("networkx")
    
import networkx as nx
from pyvis.network import Network
import random

from config import cfg

def graph_visual_with_html(graph_path, save_path):
    # Load the GraphML file
    G = nx.read_graphml(graph_path)

    # Create a Pyvis network
    net = Network(height="100vh", notebook=True, cdn_resources='in_line')

    # Convert NetworkX graph to Pyvis network
    net.from_nx(G)


    # Add colors and title to nodes
    for node in net.nodes:
        node["color"] = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        if "description" in node:
            node["title"] = node["description"]

    # Add title to edges
    for edge in net.edges:
        if "description" in edge:
            edge["title"] = edge["description"]

    # Save and display the network
    print("Knowledge graph saved to:")
    net.show(save_path)

if __name__ == '__main__':
    graph_path = cfg.file.working_dir + "/graph_chunk_entity_relation.graphml"
    save_path = cfg.file.working_dir + "/knowledge_graph.html"
    graph_visual_with_html(graph_path, save_path)
    
