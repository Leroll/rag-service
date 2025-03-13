# RAG Service 🌟
[![Version](https://img.shields.io/badge/version-0.2.0-blue)](https://github.com/Leroll/rag-service/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Cloud-deployed RAG Service API** 

- 云原生RAG服务API，基于lightRAG构建的即插即用知识增强生成系统，一键可用。
- 支持多格式文档处理与流式响应。


# 安装指南
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


# docker部署相关

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
export OLLAMA_MODELS=/app/ollama_models  >> ~/.bashrc # 更改model位置
source ~/.bashrc
rm ollama-linux-amd64.tgz 

# 2. 安装服务
pip config set global.index-url http://maven.paic.com.cn/repository/pypi/simple
pip config set install.trusted-host maven.paic.com.cn

tar xzvf rag-service_vx.x.x.tar.gz
rm rag-service_vx.x.x.tar.gz

cd rag-service/lightRAG
pip install -e .
cd ..
pip install -r requirements.txt

# 3. 导入相关raw-docs


# 4. 验证服务
./scripts/start.sh
./scripts/run_test.sh
./scripts/shutdown.sh
```


## 2. 部署
使用这种方式改起来方便点
```
# 1. 启动参数
sleep infiity

# 2. value.yaml配置
container:
    port: 50051
env:
    env_profile:prod
terminal: true


# 3. 进入镜像后
ln -s /nas/rag-service/ollama_models /app/ollama_models
./script/start.sh
```


# 服务管理
```
./scripts/start.sh  # 启动项目
./scripts/shutdown.sh  # 关闭项目

# 清理
./scripts/clean_log.sh  # 清空当前日志
./scripts/clean_rag.sh  # 清空rag数据


# 接口测试
./scripts/run_test.sh  
```

# LOGS
2025-02-27 v0.2.0 解决一系列bug，完善服务各模块，自测模块，日志模块

2025-02-25 v0.1.4，bug-fix, 修复tiktoken依赖网络下载的bug 
2025-02-25 v0.1.3，完成对老旧接口的街容 
2025-02-24 v0.1.2，完成对流式回复的支持 
2025-02-23 v0.1.1，完成对各种类型文件的支持，包括excel 
2025-02-23 v0.1.0，完成基础的rag服务各项功能  


# TODO
- [x] 完成初始系统搭建
- [x] 完成对excel的支持
- [x] 完成对SSE流式回复的支持
- [x] 完成对历史数据输入输出格式的兼容
- [x] tag - v0.2.0 - v2025-02-27
    - [x] 浏览器跨域问题
    - [x] 流式回复累加回复
    - [x] bug-fix， 修复"1"，"2"这种query回复报错的问题
    - [x] 新增一键删除rag库的脚本
    - [x] 增加测试案例机制
    - [x] 完善日志功能
    - [x] 完成镜像打包制式化pipeline
- [x] tag - v0.2.1 - v2025-03-27
    - [x] /v1/query接口，直接返回 回复字符串，不再进行字典，json包裹
    - [x] 拆分各个测试脚本，模块化
    - [ ] 新增html富文本清洗脚本
- [ ] tag - v0.3.0 - v遥遥无期
    - [ ] 处理ollama lightRAG的日志分割问题
    - [ ] Docker 时间优化
    - [ ] 完成 DockerFile 一键脚本

 

