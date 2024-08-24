import json
import jsonlines
from logger_setup import logger
import os
import globle_var as gl

def read_page_hash() -> set:
    """ 从文件读取已爬取的页面哈希值用来去重 """
    page_hash = set()
    try:
        with open('hash.txt', 'r', encoding='utf-8') as f:
            for line in f:# 逐行读取
                line = line.strip()# 去掉每行头尾空白
                if line:# 如果不是空行
                    page_hash.add(line)
    except:
        pass
    return page_hash

def saveline_page_hash(page_hash:str):
    """ 
    保存单个页面哈希值到文件 
    page_hash: 一行哈希值
    """
    with open("hash.txt", "a", encoding='utf-8') as file:
        file.write(page_hash + "\n")

def read_searched_url() -> set:
    """ 从文件读取已爬取的URL用来去重 """
    searched_url = set()
    num = 0
    try:
        with open('searched_url.txt', 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:# 逐行读取
                line = line.strip()# 去掉每行头尾空白
                if line:# 如果不是空行
                    searched_url.add(line)
                num += 1
    except Exception as e:
        logger.error(f"读取已爬取的URL失败，错误信息：{e}")
        logger.error(f"错误行数：{num}")
        pass
    logger.info(f"读取到{num}个已爬取的URL")
    return searched_url

def saveline_searched_url(url:str):
    """ 
    保存单个页面链接到文件 
    url: 一行URL
    """
    with open("searched_url.txt", "a", encoding='utf-8') as file:
        file.write(f"{url}\n")



def save_page(filename:str, page:str, ext:str):
    """ 
    保存单个页面到文件 
    page: 页面内容
    """
    # 创建保存HTML文件的目录
    domain = gl.domain
    save_dir = f"./{ext}/{domain}"
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, f"{filename}.{ext}")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(page)




def saveline_file_link(file_link:list):
    """ 
    保存单个文件链接到文件(jsonl格式) 
    file_link: 来源链接+包含的文件链接
    """
    with jsonlines.open('file_links.jsonl', mode='a') as writer:
        writer.write(file_link)

def read_file_links() -> list:
    """ 从文件读取需要下载的文件链接(读取为set) """
    file_links = []
    with jsonlines.open('file_links.jsonl', mode='r') as reader:
            for obj in reader:
                file_links.append(obj)

    return file_links



def saveline_files_mask(file_link:list):
    ''' 
    储存已下载的文件链接，与全部链接做差实现断点重续 
    file_link: 已下载的文件链接
    '''
    with jsonlines.open('files_mask.jsonl', mode='a') as writer:
        writer.write(file_link)

def read_files_mask() -> set:
    ''' 读取已下载的文件链接 '''
    files_mask = set()
    with jsonlines.open('files_mask.jsonl', mode='r') as reader:
        for obj in reader:
            files_mask.add(obj)

    return files_mask



def saveline_page_link(new_links: set):
    new_links = list(new_links)
    """ 
    保存单个页面链接到文件(jsonl格式) 
    page_link: 一行页面链接
    """
    with jsonlines.open('page_links.jsonl', mode='a') as writer:
        writer.write(new_links)

def read_page_links() -> set:
    """ 从文件读取需要下载的页面链接(读取为set) """
    page_links = set()
    with jsonlines.open('page_links.jsonl', mode='r') as reader:
        for links in reader:
            page_links.update(links)

    return page_links




def saveline_files_mapping(file_mappping:dict):
    """ 
    保存一行文件映射关系到文件(jsonl格式) 
    file_mappping: 一个页面与其url、包含文件的字典
    """
    try:
        with jsonlines.open("files_mappping.jsonl", mode="a") as file:
            file.write(file_mappping)
    except Exception as e:
        logger.error(f"[保存文件映射失败] 错误信息：{e}")



def record_error_url(reason:str, url:str):
    """ 
    记录访问出错的URL 
    reason: 出错原因
    url: 出错URL
    """
    with open("error_url.txt", "a", encoding='utf-8') as file:
        file.write(f"{reason}:{url}\n")



def clear_history(files:bool = True, records:bool = True):
    """ 
    清理所有爬取的历史记录与保存的文件 
    files: 是否清理文件
    records: 是否清理爬取记录
    """    
    if files:
        # 删除./html目录
        for root, dirs, files in os.walk("./html", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        # 删除./files目录下的所有文件
        for root, dirs, files in os.walk("./files", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
    if records:
        # 清空已爬取的链接
        with open("searched_url.txt", "w", encoding='utf-8') as file:
            file.write("")
        # 清空已爬取页面的哈希值
        with open("hash.txt", "w", encoding='utf-8') as file:
            file.write("")
        # 清空待爬取的链接
        with open("page_links.jsonl", "w") as file:
            file.write("")
        # 清理链接列表文件
        with open("file_links.jsonl", "w") as file:
            file.write("")
        # 清理已下载页面记录
        with open("files_mask.jsonl", "w") as file:
            file.write("")
        # 清理映射文件
        with open("files_mappping.jsonl", "w") as file:
            file.write("")
        # 清理ssl错误记录
        with open("error_url.txt", "w", encoding='utf-8') as file:
            file.write("")

def create_config_files():
    """ 
    创建配置文件 
    """
    # 创建保存文件的目录
    os.makedirs("./html", exist_ok=True)
    os.makedirs("./files", exist_ok=True)
    # 创建配置文件（如果存在则不覆盖）
    open("searched_url.txt", "a").close()
    open("hash.txt", "a").close()
    open("page_links.jsonl", "a").close()
    open("file_links.jsonl", "a").close()
    open("files_mask.jsonl", "a").close()
    open("files_mappping.jsonl", "a").close()
    open("error_url.txt", "a").close()


