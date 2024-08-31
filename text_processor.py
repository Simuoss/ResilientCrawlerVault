import os
from bs4 import BeautifulSoup
import re
import html2text
from bs4 import Comment
import hashlib
from logger_setup import logger
import config as config

def wash_url(url:str) -> str:
    """ 
    去掉 URL 中的特殊字符以便作为文件名 
    url: URL字符串
    """
    # 清洗各类特殊字符
    pattern = r'[\\/:*?"<>|/]|[\0\b\f\n\r\t]'
    # 使用正则表达式进行替换
    sanitized = re.sub(pattern, '_', url)
    return sanitized


def md_html2text(html:str) -> str:
    """ 
    使用html2text将HTML转换为Markdown
    html: HTML字符串
    如果处理失败，则返回空字符串
    """
    try:
        markdown = html2text.html2text(html)
    except Exception as e:
        logger.warn(f"转换md格式过程出错: {e}")
        logger.info(f"尝试用BeautifulSoup清理html...")
        soup = BeautifulSoup(html, 'html.parser')
        cleaned_html = soup.prettify()
        
        # 将清理后的 HTML 转换为 Markdown
        try:
            markdown = md_html2text(cleaned_html)
        except Exception as e:
            logger.error(f"仍然报错: {e}")
            logger.info(f"跳过此页面的md转换")
            return html
    
    return markdown

def my_html2text(html:str) -> str:
    """ 
    使用正则表达式去除HTML标签 
    html: HTML字符串
    如果处理失败，则返回原字符串
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        # 用bs4删掉所有标签属性
        for tag in soup.find_all(True):
            tag.attrs = {}
        # 用bs4删掉所有<script>标签与内部内容
        [s.extract() for s in soup('script')]
        # 用bs4删掉所有<style>标签与内部内容
        [s.extract() for s in soup('style')]
        # 用bs4删掉所有注释
        comments = soup.findAll(string=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
        # 用bs4删掉所有textarea标签
        [s.extract() for s in soup('textarea')]

        html = soup.get_text()
        # 删除多余的空行
        html = re.sub(r'\n+', '\n', html)
    except Exception as e:
        logger.error(f"清理html过程出错: {e}")
        logger.error(f"此页面无法去除html元素，按原样保存")
    
    # 返回纯文本
    return html

def stable_hash(html:str) -> str:
    """ 计算仅和内容有关的稳定哈希值 """
    hash_html = hashlib.sha256()
    # 处理成字符串
    hash_html.update(html.encode('utf-8'))
    # 返回哈希值
    return hash_html.hexdigest()

def remove_specific_tags(html:str) -> str:
    """ 删除指定class标签 """
    soup = BeautifulSoup(html, 'html.parser')
    # 删除指定class标签
    tags = config.tags
    # 删除指定标签
    for tag in tags:
        [s.extract() for s in soup.find_all(class_=tag)]
        [s.extract() for s in soup.find_all(id=tag)]
    
    # 模糊匹配foot和head
    tags_fuzzy = config.tags_fuzzy
    for tag in tags_fuzzy:
        [s.extract() for s in soup.find_all(class_=re.compile(tag))]
        [s.extract() for s in soup.find_all(id=re.compile(tag))]
    
    # 删除包含超链接或相关内容的标签
    hyperlinked_tags = config.hyperlinked_tags
    for tag in hyperlinked_tags:
        for element in soup.find_all(tag):
            element.extract()

    # 返回清理后的html
    return soup.prettify()


if __name__ == "__main__":
    you_havenot_changed_this_file = True
    if you_havenot_changed_this_file:
        print("【警告】为了避免无意中执行该文件，请确认下方的源目录和目标目录无误后，修改you_havenot_changed_this_file变量为False后再运行")
        exit()
    origin_dir = './html/'
    md_dir = './md/'
    os.makedirs(md_dir, exist_ok=True)
    # 遍历目录并处理html文件。放在./md/chd.edu.cn/目录下
    for root, dirs, files in os.walk(origin_dir):
        for name in files:
            if name.endswith('.html'):
                with open(os.path.join(root, name), 'r', encoding='utf-8') as file:
                    html = file.read()
                    # 转换为md格式
                    html = remove_specific_tags(html)
                    html = md_html2text(html)
                    md = my_html2text(html)
                    # 写入文件
                    with open(os.path.join(md_dir, name.replace('.html', '.md')), 'w', encoding='utf-8') as file:
                        file.write(md)
                    print(f"{name}转换完成")

def is_exclusions(url: str) -> bool:
    """ 检查连接是否符合排除特征 """
    # 排除特征
    for exclusion in config.exclusions:
        # 检测字符串
        if exclusion in url:
            return True
    return False