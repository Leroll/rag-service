# get_config.py
import argparse
import sys
from config import cfg  

if __name__ == "__main__":
    """用于shell脚本获取相关cfg配置信息
    """
    parser = argparse.ArgumentParser(description="Get configuration values from config.py")
    parser.add_argument('var', type=str, help="The configuration variable to retrieve")
    args = parser.parse_args()

    try :
        print(eval(f"cfg.{args.var}"))
    except AttributeError:
        print(f"Error: Configuration variable '{args.var}' not found", file=sys.stderr)
        sys.exit(1)