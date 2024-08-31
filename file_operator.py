import json
import jsonlines
import os
import threading
from logger_setup import logger
import config as config

# 基础文件管理类
class FileManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lock = threading.Lock()  # 创建线程锁
    
    def read_as_set(self) -> set:
        """将txt文件读取为set"""
        objs = set()
        num = 0
        with self.lock:
            try:
                with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:# 逐行读取
                        line = line.strip()# 去掉每行头尾空白
                        if line:# 如果不是空行
                            objs.add(line)
                        num += 1
            except Exception as e:
                logger.error(f"读取{self.file_path}文件失败，错误信息：{e}")
                logger.error(f"错误行数：{num}")
                pass
        logger.info(f"共读取了{num}行数据")
        return objs
    
    def write(self, content: str, mode: str = 'w') -> None:
        """清空并写入内容到文件"""
        with self.lock:
            with open(self.file_path, mode, encoding='utf-8') as f:
                f.write(content)

    def append(self, content: str) -> None:
        """追加内容到文件（无换行）"""
        with self.lock:
            with open(self.file_path, 'a', encoding='utf-8') as f:
                f.write(content)

    def clear(self) -> None:
        """清空文件内容"""
        with self.lock:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.truncate()

# JSON Lines 文件管理类
class JsonLinesManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lock = threading.Lock()  # 创建线程锁
    
    def write(self, obj: any) -> None:
        """写入一行对象到 JSON Lines 文件"""
        with self.lock:
            with jsonlines.open(self.file_path, mode='a') as writer:
                writer.write(obj)
    
    def clear(self) -> None:
        """清空文件内容(完全清空，不留[])"""
        with self.lock:
            with jsonlines.open(self.file_path, mode='w') as writer:
                pass


# 各种具体文件管理类
class PageHashFile(FileManager):
    def __init__(self):
        super().__init__('hash.txt')
    
    def read(self) -> set:
        """ 从文件读取已爬取的页面哈希值用来去重 """
        return self.read_as_set()

    def save_line(self, page_hash: str) -> None:
        """ 
        保存单个页面哈希值到文件 
        page_hash: 一行哈希值
        """
        self.append(f"{page_hash}\n")

class SearchedUrlFile(FileManager):
    def __init__(self):
        super().__init__('searched_url.txt')
    
    def read(self) -> set:
        """ 从文件读取已爬取的URL用来去重 """
        return self.read_as_set()

    def save_line(self, url: str) -> None:
        """ 
        保存单个页面链接到文件 
        url: 一行URL
        """
        self.append(f"{url}\n")

def save_page(filename:str, page:str, ext:str):
    """ 
    保存单个页面到文件 
    page: 页面内容
    """
    # 创建保存HTML文件的目录
    domain = config.domain
    save_dir = f"./{ext}/{domain}"
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, f"{filename}.{ext}")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(page)

class JsonLinesFile(JsonLinesManager):
    def __init__(self, file_path: str):
        super().__init__(file_path)
    
    def save_line(self, obj: any) -> None:
        """ 保存单个对象到JSON Lines文件 """
        self.write(obj)
    
    def read_as_set(self) -> set:
        """ 读取JSON Lines文件并转换为集合 """
        objs = set()
        with jsonlines.open(self.file_path, mode='r') as reader:
            for obj in reader:
                objs.update(obj)
        
        return objs
    
    def read_as_list(self) -> list:
        """ 读取JSON Lines文件并转换为列表 """
        objs = []
        with jsonlines.open(self.file_path, mode='r') as reader:
            for obj in reader:
                objs.append(obj)
        
        return objs

# 各种具体 JSON Lines 文件管理类
class FileLinksFile(JsonLinesFile):
    def __init__(self):
        super().__init__('file_links.jsonl')

    def read(self) -> list:
        """ 从文件读取需要下载的文件链接(读取为list) """
        return self.read_as_list()
    
    def save_line(self, file_link: list) -> None:
        """ 
        保存单个文件链接到文件(jsonl格式) 
        file_link: 来源链接+包含的文件链接
        """
        return super().save_line(file_link)

class PageLinksFile(JsonLinesFile):
    def __init__(self):
        super().__init__('page_links.jsonl')
    
    def read(self) -> set:
        """ 从文件读取已爬取的页面链接用来去重(读取为set) """
        return self.read_as_set()
    
    def save_line(self, urls: set) -> None:
        """ 
        保存单个页面链接到文件(jsonl格式) 
        url: 一行URL
        """
        urls = list(urls)
        return super().save_line(urls)

class FilesMaskFile(JsonLinesFile):
    def __init__(self):
        super().__init__('files_mask.jsonl')
    
    def read(self) -> set:
        """ 读取已下载过文件的页面链接，用来去重(读取为set) """
        return self.read_as_set()
    
    def save_line(self, url: str) -> None:
        """ 
        保存单个已下载过文件的页面链接到文件(jsonl格式) 
        url: 一行URL
        """
        return super().save_line(url)

class FilesMappingFile(JsonLinesFile):
    def __init__(self):
        super().__init__('files_mappping.jsonl')

    def save_line(self, obj: dict) -> None:
        """
        保存单个文件映射到文件(jsonl格式)
        字典格式示例
        {
            "http___www.hdu.edu.cn_761_list.htm": {
                "url": "http://www.hdu.edu.cn/761/list.htm",
                "src": ["./files/www.hdu.edu.cn/1.pdf", "./files/www.hdu.edu.cn/2.jpg"]
            }
        }
        实现从网页文件直接查询到其所属的资源路径
        """
        return super().save_line(obj)

class ErrorUrlFile(FileManager):
    def __init__(self):
        super().__init__('error_url.txt')

    def record_error(self, reason: str, url: str) -> None:
        """ 
        记录访问出错的URL 
        reason: 出错原因
        url: 出错URL
        """
        self.append(f"{reason}:{url}\n")

searched_url_file = SearchedUrlFile()
page_hash_file = PageHashFile()
file_link_file = FileLinksFile()
page_link_file = PageLinksFile()
files_mask_file = FilesMaskFile()
files_mapping_file = FilesMappingFile()
error_url_file = ErrorUrlFile()



# 实用函数
def clear_history(files: bool = True, records: bool = True) -> None:
    """ 
    清理所有爬取的历史记录与保存的文件 
    files: 是否清理文件
    records: 是否清理爬取记录
    """
    if files:
        # 删除 ./html 和 ./files 目录
        for directory in ['./html', './files', './md']:
            for root, dirs, files in os.walk(directory, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
    if records:
        # 创建一个包含所有需要清空的文件管理对象的列表
        file_managers = [
            SearchedUrlFile(),
            PageHashFile(),
            PageLinksFile(),
            FileLinksFile(),
            FilesMaskFile(),
            FilesMappingFile(),
            ErrorUrlFile(),
        ]
        for fm in file_managers:
            fm.clear()  # 清空文件内容
            logger.debug(f"清空文件: {fm.file_path}")

def create_config_files() -> None:
    """ 
    创建配置文件 
    """
    # 创建保存文件的目录
    os.makedirs("./html", exist_ok=True)
    os.makedirs("./files", exist_ok=True)
    os.makedirs("./md", exist_ok=True)
    # 创建配置文件（如果存在则不覆盖）
    for file in ['searched_url.txt', 'hash.txt', 'page_links.jsonl', 'file_links.jsonl', 'files_mask.jsonl', 'files_mappping.jsonl', 'error_url.txt']:
        open(file, 'a').close()
