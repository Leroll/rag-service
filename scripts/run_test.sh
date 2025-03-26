#!/bin/bash

# 可以在清空log，rag的情况下运行测试，以避免缓存的影响，该测试脚本会测试所有的服务接口
python client/test_all.py

# 检查 Python 脚本是否成功执行
echo "---------------------------------"
if [ $? -eq 0 ]; then
    echo "Python 脚本执行完毕"
else
    echo "Python 脚本执行失败"
fi