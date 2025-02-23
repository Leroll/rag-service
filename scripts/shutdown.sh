#!/bin/bash

# 停止 ollama 服务
echo "-----------------------------"
echo "正在关闭 Ollama 服务..."

OLLAMA_PID=$(ps -ef | grep 'ollama serve' | grep -v grep | awk '{print $2}')
if [ ! -z "$OLLAMA_PID" ]; then
  echo "找到 ollama serve (PID: $OLLAMA_PID)，发送终止信号..."
  kill -TERM "$OLLAMA_PID"  # 使用 SIGTERM 优雅终止
  sleep 5  # 等待 5 秒，让子进程有时间退出
  echo "已停止 ollama serve (PID: $OLLAMA_PID)"
else
  echo "ollama serve 未运行。"
fi

# 检查并清理残留的 ollama_llama_server 子进程
if pgrep -f "ollama_llama_server" > /dev/null; then
  echo "发现残留的 ollama_llama_server 进程，正在清理..."
  pkill -f "ollama_llama_server"  # 先尝试优雅终止
  sleep 2
  if pgrep -f "ollama_llama_server" > /dev/null; then
    echo "仍有子进程未退出，强制终止..."
    pkill -9 -f "ollama_llama_server"  # 如果还未退出，强制杀掉
  fi
  echo "已清理所有 ollama_llama_server 进程。"
else
  echo "未发现 ollama_llama_server 残留进程。"
fi

# 停止 rag_server.py
echo "-----------------------------"
echo "正在检查 rag_server.py..."
PYTHON_PID=$(ps aux | grep 'rag_server.py' | grep -v grep | awk '{print $2}')
if [ ! -z "$PYTHON_PID" ]; then
  echo "找到 rag_server.py (PID: $PYTHON_PID)，发送终止信号..."
  kill -TERM "$PYTHON_PID"  # 使用 SIGTERM 优雅终止
  sleep 2  # 等待进程退出
  if ps -p "$PYTHON_PID" > /dev/null; then
    echo "进程未退出，强制终止..."
    kill -9 "$PYTHON_PID"  # 如果未退出，强制杀掉
  fi
  echo "已停止 rag_server.py (PID: $PYTHON_PID)"
else
  echo "rag_server.py 未运行。"
fi

echo "-----------------------------"
# 验证资源状态
echo "验证服务状态："
if pgrep -f "ollama" > /dev/null || pgrep -f "rag_server.py" > /dev/null; then
  echo "警告：仍有相关进程未关闭，请手动检查。"
else
  echo "所有服务已成功关闭。"
fi

# echo "当前显存状态："
# nvidia-smi