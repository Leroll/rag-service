import tempfile
import traceback
import openpyxl
import textract
import os
from loguru import logger


def temproary_save_file(file_content, file_extension):
    """暂时保存文件
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        logger.info(f"temporary saved | {temp_file_path}")
    except Exception as e:
        temp_file_path = None
        logger.error(f"temporary save failed | {traceback.format_exc()}")
    return temp_file_path

def read_excel(file_extension, temp_file_path):
    """读取 Excel 文件
    """
    try:
        # 使用 openpyxl 读取 Excel 文件
        workbook = openpyxl.load_workbook(temp_file_path)
        content = ""
        for sheet in workbook.sheetnames:
            worksheet = workbook[sheet]
            for row in worksheet.rows:
                for cell in row:
                    cell_value = cell.value
                    if cell_value is not None:
                        content += str(cell_value) + " "
        msg = "succ"
        logger.info(f"read excel success | {temp_file_path}")
    except Exception as e:
        content = None
        msg = "read excel failed"
        logger.error(f"read excel failed | {traceback.format_exc()}")
    return content, msg


def read_pdf_docx_pptx(file_extension, temp_file_path):
    """读取 PDF、DOCX、PPTX 等文件
    """
    try:
        # 使用 textract 提取内容
        text_content = textract.process(temp_file_path)
        content = text_content.decode('utf-8')
        msg = "succ"
        logger.info(f"read {file_extension} success | {temp_file_path}")
    except Exception as e:
        content = None
        msg = f"read {file_extension} failed"
        logger.error(f"read {file_extension} failed | {traceback.format_exc()}")
    return content, msg

def read_file(file_extension, temp_file_path):
    """读取文件内容
    """
    if file_extension == 'xlsx':  # 处理 Excel 文件 (.xlsx)
        content, msg = read_excel(file_extension, temp_file_path)
    else:  # 处理其他文件类型（如 PDF、DOCX、PPTX 等）
        content, msg = read_pdf_docx_pptx(file_extension, temp_file_path)
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
    content, msg = read_file(file_extension, temp_file_path)
    
    # 3. 删除临时文件
    os.remove(temp_file_path)
    
    return content, msg