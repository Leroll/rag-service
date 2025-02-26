# RAG Service 🌟
[![Version](https://img.shields.io/badge/version-0.1.4-blue)](https://github.com/Leroll/rag-service/releases)
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
2025-02-23 v0.1.0，完成基础的rag服务各项功能  
2025-02-23 v0.1.1，完成对各种类型文件的支持，包括excel  
2025-02-24 v0.1.2，完成对流式回复的支持  
2025-02-25 v0.1.3，完成对老旧接口的街容  
2025-02-25 v0.1.4，bug-fix, 修复tiktoken依赖网络下载的bug  


# TODO
- [x] 完成初始系统搭建
- [x] 完成对excel的支持
- [x] 完成对SSE流式回复的支持
- [x] 完成对历史数据输入输出格式的兼容
- [ ] tag - v0.2.0 - v2025-02-27
    - [x] 浏览器跨域问题
    - [x] 流式回复累加回复
    - [x] bug-fix， 修复"1"，"2"这种query回复报错的问题
    - [x] 新增一键删除rag库的脚本
    - [x] 增加测试案例机制
    - [ ] 完善日志功能
    - [ ] 完成镜像打包制式化pipeline
    - [ ] 日志按天分割，logratate

 

