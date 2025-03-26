import subprocess
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))   # 添加项目根目录到 sys.path，以便导入 config.py

from config import cfg

# ANSI escape codes for colors
RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'

def run_test_script(script_name):
    """Runs a test script and returns True if successful, False otherwise."""
    print(f"\n\n{'-'*21} Running test script: {GREEN}{script_name}{RESET} {'-'*21}")
    try:
        print(f"Running {script_name}...")
        process = subprocess.run(['python', script_name], capture_output=True, text=True, check=True)
        print(process.stdout)
        print(f"{script_name} {GREEN}PASSED{RESET}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{script_name} {RED}FAILED{RESET} with error:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"{RED}Error{RESET}: {script_name} not found.")
        return False

if __name__ == '__main__':
    test_scripts = [
        "client/health_and_version.py",
        "client/insert_text.py",
        "client/insert_file.py",
        "client/query_full.py",
        "client/query_stream.py"
    ]

    all_tests_passed = True
    for script in test_scripts:
        if not run_test_script(script):
            all_tests_passed = False

    if all_tests_passed:
        print(f"\n{GREEN}ALL TESTS PASSED!{RESET}")
    else:
        print(f"\n{RED}SOME TESTS FAILED!{RESET}")