# rag-service
Cloud-deployed RAG Service API


# 安装
```
git clone --recurse-submodules https://github.com/Leroll/rag-service.git  
cd rag-service/LightRAG
pip install -e .
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
- [x] 浏览器跨域问题
- [ ] 流式回复累加回复
- [ ] 增加测试案例机制
- [ ] 完善日志功能
- [ ] 完成镜像打包制式化pipeline
- [ ] 日志按天分割，logratate
- [ ] tag - 2025-02-26 - v0.2.0
 

