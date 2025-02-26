import os
import shutil
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 添加项目根目录到 sys.path，以便导入 config.py
from config import Config

# 获取配置
cfg = Config('./config').get_config()
working_dir = cfg.file.working_dir

# 检查目录并删除文件
if os.path.isdir(working_dir):
    print(f"正在删除 {working_dir} 下的文件...")
    for item in os.listdir(working_dir):
        item_path = os.path.join(working_dir, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
    print("删除完成")
else:
    print(f"目录 {working_dir} 不存在")