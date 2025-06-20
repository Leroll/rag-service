# 🌟 RAG Service 🌟
[![GitHub stars](https://img.shields.io/github/stars/Leroll/rag-service?style=social)](https://github.com/Leroll/rag-service/stargazers)
[![GitHub all releases](https://img.shields.io/github/downloads/Leroll/rag-service/total)](https://github.com/Leroll/rag-service/releases)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/Leroll/rag-service)](https://github.com/Leroll/rag-service/releases/latest)
[![GitHub last commit](https://img.shields.io/github/last-commit/Leroll/rag-service)](https://github.com/Leroll/rag-service/commits/main)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Cloud-deployed RAG Service API** 

- 云原生RAG服务API，基于lightRAG构建的即插即用知识增强生成系统，一键可用。
- 支持多格式文档处理与流式响应。


# 🔧 安装指南
```
# 1. 安装ollama方式
sudo tar -C /usr -xzf ollama-linux-amd64.tgz  # 离线安装方式
export OLLAMA_MODELS=/path/to/ollama_models/  # 更改model位置

# 2. 下载本项目仓库
git clone --recurse-submodules https://github.com/Leroll/rag-service.git  
cd rag-service/LightRAG
pip install -e .

# 3. 安装其他依赖包
pip install -r requirements.txt  # 另在初次运行时会自动安装一些包
```


# 🐳 docker部署相关

## 1. 建立docker镜像
```
# 进入基础镜像
docker run -it -p 50051:50051 -v /path/to/ollama_models:/app/ollama_models --gpus all --privileged leroll/cuda:12.1.0-cudnn8-devel-ubuntu22.04-py3.10

# 传输必要文件
docker cp /path/to/ollama-linux-amd64.tgz container_id:/app/  # 复制ollma文件
docker cp /path/to/rag-service_vx.x.x.tar.gz container_id:/app/  # 复制服务代码
# 复制相关 raw_docs

# 镜像内部
cd app/

# 1. 安装 ollama 
tar -C /usr -xzf ollama-linux-amd64.tgz  # root不用sudo
echo "export OLLAMA_MODELS=/app/ollama_models"  >> ~/.bashrc # 更改model位置
source ~/.bashrc
rm ollama-linux-amd64.tgz 

# 2. 安装服务
pip config set global.index-url http://xxxx/repository/pypi/simple
pip config set install.trusted-host xxxxx.com

tar xzvf rag-service_vx.x.x.tar.gz
rm rag-service_vx.x.x.tar.gz

cd rag-service/lightRAG
pip install -e .
cd ..
pip install -r requirements.txt

# 2.1 安装文件预处理模块及起支持
pip install "unstructured[all-docs]"   
sudo apt-get update && sudo apt-get install -y libreoffice  # 1. 安装主程序（包含soffice）
sudo apt-get install -y libreoffice-headless # 2. 可选：安装无头模式（适用于服务器环境）
soffice --version # 3. 验证安装

# 3. 导入相关raw-docs

# 4. 验证服务
./scripts/start.sh
./scripts/run_test.sh
./scripts/shutdown.sh
```


# 🚦 服务管理
```
./scripts/start.sh  # 启动项目
./scripts/shutdown.sh  # 关闭项目

# 清理
./scripts/clean_log.sh  # 清空当前日志
./scripts/clean_rag.sh  # 清空rag数据


# 接口测试
./scripts/run_test.sh  
```

# 🚀 版本更新

**v0.2.2 (2025-03-27)**
- 新增LightRAG工厂模式，定制化其特定功能，如naive模式，省略实体抽取与关系的构建过程，退化为向量库检索

**v0.2.1 (2025-03-27)**  
- 优化 `/v1/query` 接口直接返回字符串，不再进行字典，json包裹
- 文件预处理模块新增对 HTML/DOC 格式的支持  
- 支持多种数据结构适配不同场景  
- 拆分测试脚本为模块化结构
- 添加图谱生成脚本

**v0.2.0 (2025-02-27)**  
- 修复浏览器跨域问题  
- 流式回复累加回复
- 处理特殊字符（如 "1", "2"）导致的报错  
- 新增一键删除 RAG 数据库脚本  
- 增加测试用例和日志模块  
- 完善 Docker 镜像打包pipeline  

<details>
<summary><b>查看更早历史版本</b></summary>

**v0.1.4 (2025-02-25)**  
- 修复 tiktoken 依赖的网络下载问题  

**v0.1.3 (2025-02-25)**  
- 兼容老旧接口数据格式  

**v0.1.2 (2025-02-24)**  
- 支持流式回复（SSE）  

**v0.1.1 (2025-02-23)**  
- 新增对 Excel 文件的解析支持  

**v0.1.0 (2025-02-23)**  
- 基础 RAG 服务功能上线  

</details>


# 🎯 TODO 
- [ ] tag - v0.3.0 - v2025-xx-xx
    - [ ] 增加本地离线raw_docs导入
    - [ ] 处理ollama lightRAG的日志分割问题
    - [ ] Docker 时间优化
    - [ ] 完成 DockerFile 一键脚本