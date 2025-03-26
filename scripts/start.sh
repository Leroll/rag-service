#!/bin/bash
#####################################
# 用法：./scripts/start.sh -v
#   支持 -v 参数，启用详细日志模式，否则启动server的日志会输出到 /dev/null
#####################################

# 定义日志文件和 PID 文件路径
NOHUP_LOG="/dev/null"  # 默认值
OLLAMA_LOG="logs/ollama.log"
OLLAMA_PID_FILE="logs/ollama.pid"
SERVER_PID_FILE="logs/server.pid"

# 检查是否传入 -v 参数
while getopts "v" opt; do
  case $opt in
    v)
      NOHUP_LOG="logs/nohup.log"
      echo "使用详细日志模式"
      ;;
    \?)
      echo "无效参数: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# 确保 logs 目录存在
mkdir -p logs

# 检查是否已有服务运行
if [ -f "$OLLAMA_PID_FILE" ] && ps -p "$(cat "$OLLAMA_PID_FILE")" > /dev/null; then
  echo "Ollama 服务已在运行（PID: $(cat "$OLLAMA_PID_FILE")），请先关闭后再启动。"
  exit 1
fi
if [ -f "$SERVER_PID_FILE" ] && ps -p "$(cat "$SERVER_PID_FILE")" > /dev/null; then
  echo "Python 服务已在运行（PID: $(cat "$SERVER_PID_FILE")），请先关闭后再启动。"
  exit 1
fi

# 启动 ollama 服务
echo "-----------------------------"
nohup ollama serve >> "${OLLAMA_LOG}" 2>&1 &
OLLAMA_PID=$!
echo "$OLLAMA_PID" > "$OLLAMA_PID_FILE"
echo "Ollama 服务已启动，PID: ${OLLAMA_PID}，日志输出至: ${OLLAMA_LOG}"

# 等待并检查 ollama 是否启动成功
sleep 2
if ps -p "$OLLAMA_PID" > /dev/null; then
  echo "Ollama 服务启动成功。"
else
  echo "Ollama 服务启动失败，请检查日志: ${OLLAMA_LOG}"
  exit 1
fi

# 启动 python 服务
echo "-----------------------------"
nohup python server.py > ${NOHUP_LOG} 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$SERVER_PID_FILE"
echo "server 服务已启动，PID: ${SERVER_PID} "

# 等待并检查 python 服务是否启动成功
sleep 2
if ps -p "$SERVER_PID" > /dev/null; then
  echo "server 服务启动成功。"
else
  echo "server 服务启动失败"
  exit 1
fi

echo "所有服务已启动完成。"