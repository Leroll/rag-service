from bs4 import BeautifulSoup
import html


"""
完成对html文件的清理工作，去除html标签，处理html实体等
"""
def clean_html_with_bs(html_text):
    # 创建BeautifulSoup对象
    soup = BeautifulSoup(html_text, "html.parser")
    
    # 提取纯文本并处理HTML实体
    text = soup.get_text(separator=' ', strip=True)
    
    # 处理HTML实体转义（如 &amp; -> &）
    return html.unescape(text)


if __name__ == "__main__":
    # 使用示例
    dirty_html = "<div><h1>Title</h1><p>Paragraph with <em>emphasis</em> &amp; entities</p></div>"
    clean_text = clean_html_with_bs(dirty_html)
    print(clean_text)
    # 输出: Title Paragraph with emphasis & entities