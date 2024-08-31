from typing import Tuple, Union

import chardet
import config
from file_operator import save_page, searched_url_file, page_hash_file, file_link_file, page_link_file, files_mask_file, files_mapping_file, error_url_file
from logger_setup import logger
import globle_var as gv
from text_processor import wash_url, md_html2text, my_html2text, stable_hash, remove_specific_tags, is_exclusions
# 导入所需的库
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
from bs4 import BeautifulSoup
from urllib.parse import ParseResultBytes, urlparse, urljoin
import requests

import os



# TODO:
# [x] 1. 处理跨域资源（比如在线文档、表格）
# [?] 2. 处理动态加载的内容
# [-] 3. 清理js、php、css等内容无关的链接
# [-] 4. 更新哈希方式
# [-] 5. 更新json->jsonlines

def create_driver() -> Edge:
    """ 创建 Edge WebDriver 实例 """
    # 设置 Edge WebDriver 的路径
    edge_driver_path = "./chromedriver/msedgedriver.exe"  # 替换为你的 Edge WebDriver 的路径

    edge_options = EdgeOptions()
    edge_options.use_chromium = True
    # 设置无界面模式，也可以添加其它设置
    edge_options.add_argument('headless')
    edge_options.add_argument('--log-level=3')  # 仅显示严重错误
    driver = Edge(options=edge_options)

    return driver

def driver_get_page(url:str, driver:Edge):
    """ 
    使用 Selenium 获取HTML页面 
    url: 页面链接
    driver: Edge WebDriver 实例
    """
    logger.debug(f"正在使用Selenium获取页面: {url}")
    driver.get(url)
    return driver.page_source

def fetch_url(url:str, headers:dict, forbidden_domain:str, verify: bool=False, retry: int=5) -> Union[requests.Response, None]:
    """ 
    处理重定向 
    url: 请求的URL
    headers: 请求头
    forbidden_domain: 禁止的域名
    """
    # 从左往右，遇到第一个<符号，截断，防止出现“https://dsai.chd.edu.cn/<span style='color:red;font-size:9pt'>转换链接错误</span>”
    url = url.split('<')[0]
    with gv.lock_searched_url:
        if url in gv.searched_url and retry == 5:
            logger.debug(f"[在重定向时跳过已爬取url] ：{url}")
            return None
        else:
            logger.debug(f"[在重定向时添加新链接到已爬取url] ：{url}")
            gv.searched_url.add(url)
            searched_url_file.save_line(url)

    try:
        response = requests.get(url = url, headers = headers, allow_redirects=False,timeout=(2, 4), verify = verify)  # 禁用自动重定向
        logger.debug(response)
        if response.status_code == 404:
            logger.warning(f"[404 Not Found]: {url}")
            error_url_file.record_error("404", url)
            return None
        
        if response.status_code in [301, 302]:  # 检测重定向状态码
            verify = True
            redirect_url = response.headers.get('Location')
            # 如果redirect_url不以http开头
            if not redirect_url.startswith(('http://', 'https://')):
                redirect_url = urljoin(url, redirect_url)  # 将相对 URL 转换为绝对 URL
            logger.debug(f"[重定向到] {redirect_url}")

            # 检查是否有出界的域名
            if not urlparse(redirect_url).netloc.endswith(forbidden_domain):
                logger.warning(f"[终止请求] 重定向到外部域名")
                return None
            
            # 检查重定向目标里是否包含gl.exclusions中的字符串
            if is_exclusions(redirect_url):
                logger.warning(f"[终止请求] 重定向到禁止的域名")
                #print(f"text:{response.text}\n headers:{response.headers}\n url:{response.url}\n status_code:{response.status_code}\n history:{response.history}\n")
                return None
            else:
                return fetch_url(redirect_url, headers, forbidden_domain, verify)  # 可以递归执行重定向
        else:
            return response
    except requests.exceptions.ReadTimeout:
        logger.error("请求失败：连接超时（Read timed out）")
        error_url_file.record_error("Timeout", url)
        return None
    except requests.exceptions.SSLError as e:
        logger.warning(f"请求失败：SSL 错误（{e}）")
        if retry > 0:
            return fetch_url(url, headers, forbidden_domain, verify=False,retry=retry-1)  # 可以递归执行重定向
        error_url_file.record_error("SSL", url)
        return None
    except requests.exceptions.ProxyError as e:
        logger.warning(f"请求失败：代理错误（{e}）")
        error_url_file.record_error("Proxy", url)
        return None
    except requests.RequestException as e:
        logger.error(f"请求失败: {e}")
        error_url_file.record_error("Others", url)
        return None

def requests_get_page(url:str) -> Union[str, None]:
    """ 使用 requests 获取HTML页面 """
    # 设置请求头
    headers = config.request_headers
    headers['host'] = urlparse(url).netloc
    logger.debug(f"正在使用requests获取页面: {url}")
    # 发起请求并获取页面HTML
    #response = requests.get(url, headers=headers,timeout=(2, 4))
    response = fetch_url(url, headers, config.domain)
    if response == None:
        return None
    response.encoding = chardet.detect(response.content)['encoding']# 自动检测编码
    return response.text

def is_file_url(parsed_url: ParseResultBytes, type='text') -> bool:
    """ 判断 URL 是否指向文件 """
    if type == 'text':
        return parsed_url.path.endswith(config.text_tails)
    else:
        return parsed_url.path.endswith(config.file_tails)

def extract_links(url: str, html: str, domain: str=config.domain) -> tuple[set, list]:
    """ 从页面中提取所有链接并添加进任务栈 """
    page_links = set()
    files_in_page = [url]
    files_info = []
    status = 'start'

    soup = BeautifulSoup(html, "html.parser")
    try:
        status = 'a'
        # 提取 <a> 标签中的 href 属性
        links = soup.find_all("a", href=True)
        for link in links:
            href = link['href']
            full_url = urljoin(url, href)
            parsed_href = urlparse(full_url)

            # print(f"{type(full_url)} : {full_url}")
            if is_file_url(parsed_href):
                files_info.append(full_url)

            # 检查是否属于同一域名
            elif not is_file_url(parsed_href,"all") and parsed_href.netloc.endswith(domain):
                page_links.add(full_url)
        '''
        status = 'img'
        # 提取 <img> 标签中的 src 属性
        for tag in soup.find_all('img', src=True):
            src = tag['src']
            full_url = urljoin(url, src)
            parsed_href = urlparse(full_url)
            #print(f"{type(full_url)} : {full_url}")
            if is_file_url(parsed_href):
                files_info.append(full_url)
        '''
        status = 'link'
        # 提取 <link> 标签中的 href 属性
        for tag in soup.find_all('link', href=True):
            href = tag['href']
            full_url = urljoin(url, href)
            parsed_href = urlparse(full_url)
            if is_file_url(parsed_href):
                files_info.append(full_url)
        '''
        status = 'script'
        # 提取 <script> 标签中的 src 属性
        for tag in soup.find_all('script', src=True):
            src = tag['src']
            full_url = urljoin(url, src)
            parsed_href = urlparse(full_url)
            if is_file_url(parsed_href):
                files_info.append(full_url)
        '''
        status = 'iframe'
        # 提取 <iframe> 标签中的 src 属性
        for tag in soup.find_all('iframe', src=True):
            src = tag['src']
            full_url = urljoin(url, src)
            parsed_href = urlparse(full_url)
            if is_file_url(parsed_href):
                files_info.append(full_url)
    except Exception as e:
        logger.error(f"从 {full_url} 中提取 <{status}> 标签时出错: {e} ")
        logger.error(f"跳过此页面的链接提取")
        return
    
    files_in_page.append(files_info)
    return page_links, files_in_page


# 返回两个元组，或者None
def crawl_and_save(url: str, func: callable, driver=None) -> Union[tuple[set, list], None]:
    """ 爬取页面并保存为Markdown文件，同时提取页面中的链接加入任务栈 """
    page_links = []
    file_links = []

    # 调用func获取页面HTML
    if driver == None:
        html = requests_get_page(url)
    else:
        html = func(url,driver)
    
    # 如果获取失败则返回
    if html == None:
        logger.warning(f"[返回了空页面] 链接：{url}")
        return None
    
    md = remove_specific_tags(html)   # 删除指定标签，如footer、sidebar等
    md = md_html2text(md)           # 将可转换部分转换为markdown
    md = my_html2text(md)           # 去除其它html元素

    # 获取页面的哈希值，如果已经爬取过则直接返回
    md_hash = stable_hash(md)
    with gv.lock_page_hash:
        if md_hash in gv.page_hash:
            logger.debug(f"[新链接但内容已存在] 页面哈希：{md_hash}")
            return None
        
        # 保存哈希值
        gv.page_hash.add(md_hash)
    page_hash_file.save_line(md_hash)
    

    # 保存HTML到指定文件
    file_name = wash_url(url)
    save_page(file_name, html, 'html')
    # 保存md文件
    if config.trans_md:
        save_page(file_name, md, 'md')

    # 提取页面所有链接
    page_links, file_links = extract_links(url, html, config.domain)
    
    return page_links, file_links



# 返回一个()
def crawl_recursive(url:str, driver) -> int:
    """ 
    单条爬取任务处理 
    url: 页面链接
    driver: Edge WebDriver 实例，若为None则使用requests库
    返回：本轮新增的页面链接数量
    """
    pbar_add = 0

    # 检查是否已经爬取过
    with gv.lock_searched_url:
        if url in gv.searched_url:
            logger.debug(f"[跳过已爬取url] ：{url}")
            return pbar_add
    if is_exclusions(url):
        logger.debug(f"[跳过排除url] ：{url}")
        return pbar_add
    
    # 爬取并保存页面
    logger.info(f"[新页面，开始爬取] 链接: {url}")
    try:
        rt = crawl_and_save(url, driver)
    except Exception as e:
        logger.error(f"[因为意外原因爬取失败] 链接: {url} 错误: {e}")
        rt = None

    # 如果爬取失败则直接结束
    if rt is None:
        return pbar_add
    
    # 提取页面中的链接
    logger.info(f"[新页面，已爬取] 链接: {url}")
    page_links, file_links = rt
    # 将新页面链接加入待爬取列表
    if page_links:
        with gv.lock_page_links:
            new_links = page_links - gv.searched_url
        if new_links:
            page_link_file.save_line(new_links)
            with gv.lock_page_links:
                ori_num = len(gv.page_links)
                gv.page_links.update(new_links)    # 将新链接加进待爬取列表（set自动去重）
                pbar_add = len(gv.page_links) - ori_num  # 重新设置 total 值  

    # 将新文件链接加入待下载列表            
    if file_links[1]:
        file_link_file.save_line(file_links)
        with gv.lock_file_links:
            gv.file_links.append(file_links)       # 将新文件链接添加到待下载列表

    # 将当前URL添加到已爬取列表
    with gv.lock_searched_url:
        if url not in gv.searched_url:
            searched_url_file.save_line(url)
            gv.searched_url.add(url)

    return pbar_add

    


def download_file(link: str, verify = True) -> str:
    """ 下载文件并保存到本地 """
    # 获取文件名
    filename = link.split("/")[-1]
    # 去掉文件名后面的井号
    filename = filename.split("#")[0]
    # 文件名转换为中文
    filename = requests.utils.unquote(filename)
    # 去掉特殊字符
    filename = wash_url(filename)

    domain = urlparse(link).netloc
    domain = wash_url(domain)
    # 创建保存目录
    save_dir = f"./files/{domain}"
    file_path = f"./files/{domain}/{filename}"
    os.makedirs(save_dir, exist_ok=True)

    
    if os.path.exists(file_path):
        logger.warning(f"[跳过已下载文件] {link}")
        return file_path
    
    # 下载文件
    try:
        logger.info(f"[下载文件] 链接：{link}")
        # 发送HTTP GET请求
        response = requests.get(link, stream=True, timeout= 5, verify = verify)
        # 检查响应状态码
        if response.status_code == 200:
            # 打开本地文件以二进制将响应内容逐块写入文件
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        else:
            logger.warning(f"[下载失败，跳过此文件]：{response.status_code}")
    except requests.exceptions.ReadTimeout:
        logger.warning("请求失败：连接超时（Read timed out）")
        error_url_file.record_error("Timeout", link)
        return None
    except requests.exceptions.SSLError as e:
        logger.warning(f"请求失败：SSL 错误（{e}）")
        return download_file(link, False)       # 重新下载，关闭SSL验证(很不规范，但先用着)
    except requests.exceptions.ProxyError as e:
        logger.warning(f"请求失败：代理错误（{e}）")
        error_url_file.record_error("Proxy", link)
        return None
    except requests.RequestException as e:
        logger.error(f"请求失败: {e}")
        error_url_file.record_error("Others", link)
        return None
    
    return file_path
