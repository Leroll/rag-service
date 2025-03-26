import tempfile
import traceback
import os
from loguru import logger
from unstructured.partition.auto import partition

def temproary_save_file(file_content, file_extension):
    """暂时保存文件
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}', dir='resources/temp') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        logger.info(f"temporary saved | {temp_file_path}")
    except Exception as e:
        temp_file_path = None
        logger.error(f"temporary save failed | {traceback.format_exc()}")
    return temp_file_path
            
            
def read_file_unify(file_extension, temp_file_path):
    """读取所有文件（统一用unstructured处理）
    
    支持各种文件类型，包括 PDF、DOCX、PPTX、XLSX、TXT 等
    """
    try:
        # 统一解析文件（自动识别类型）
        elements = partition(filename=temp_file_path)
        
        # 提取文本内容（或保留结构化数据）
        content = "\n\n".join([str(e) for e in elements])
        msg = "succ"
        logger.info(f"Read {file_extension} success | {temp_file_path}")
        
    except Exception as e:
        logger.error(f"Read {file_extension} failed | {traceback.format_exc()}")
        content = None
        msg = f"read {file_extension} failed"
        
    return content, msg


def file_processing(file_content, file_extension):
    """处理文件
    
    输入为相关文件的内容和扩展名，输出为文件内容
    
    Args:
        logger: 日志记录器
        file_content: 文件内容（字节流）
        file_extension: 文件扩展名
    Returns:
        content: 文件内容, 如果处理失败则返回 None
        msg: 错误信息
    """
    # 1. 创建临时文件来存储上传的字节内容
    temp_file_path = temproary_save_file(file_content, file_extension)
    
    if temp_file_path is None:
        content = None
        msg = "无法临时保存文件，请检查文件内容"
        return content, msg
    
    # 2. 读取文件内容
    # content, msg = read_file(file_extension, temp_file_path)
    content, msg = read_file_unify(file_extension, temp_file_path)  # 统一用 unstructured 处理
    
    # 3. 删除临时文件
    os.remove(temp_file_path)
    
    return content, msg


if __name__ == "__main__":
    # 测试文件处理
    file_path = "resources/raw_docs/identity.html"
    # file_path = "resources/raw_docs/identity.txt"
    # file_path = "resources/raw_docs/identity.xlsx"
    
    with open(file_path, 'rb') as f:
        file_content = f.read()
    file_extension = file_path.split('.')[-1]
    content, msg = file_processing(file_content, file_extension)
    print('-'*42)
    print(f"Msg : {msg}")
    print(f"Content : {content}")