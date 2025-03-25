#!/bin/bash
# 定义 Python 脚本路径
# 清理对应config里面的rag缓存文件
PYTHON_SCRIPT="utils/clean_rag.py"

# 检查 Python 脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "错误: Python 脚本 $PYTHON_SCRIPT 不存在"
    exit 1
fi

# 运行 Python 脚本
python "$PYTHON_SCRIPT"

# 检查执行结果
if [ $? -eq 0 ]; then  # $? 表示上一个命令的退出状态
    echo "脚本执行成功"
else
    echo "脚本执行失败"
    exit 1
fi