import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlsplit, urlunsplit
import time

start_url = 'https://www.gradio.app/docs'

# 全局集合用于存储 URL
fetched_urls = set()
visited_urls = set()
url_404 = set()

def get_links(url):
    links = set()
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)
            #print(full_url)
            if full_url.startswith(start_url):  # 只处理相同域名的链接
                #print(full_url)
                split_url = urlsplit(full_url)
                cleaned_url = urlunsplit((split_url.scheme, split_url.netloc, split_url.path, split_url.query, ''))
                links.add(cleaned_url)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        url_404.add(url)

    return links

def crawl(start_url):
    global fetched_urls, visited_urls
    fetched_urls.add(start_url)
    to_visit = fetched_urls - visited_urls
    while to_visit:
        current_url = to_visit.pop()
        print(f"Fetching: {current_url}")
        new_links = get_links(current_url)
        # 更新已获取的 URL
        fetched_urls.update(new_links)
        # 将当前 URL 标记为已访问
        visited_urls.add(current_url)
        to_visit = fetched_urls - visited_urls

    return fetched_urls

# 设定初始 URL 

links = crawl(start_url)
links = links - url_404

# 将链接写入文件
with open('links.txt', 'w') as file:
    for link in links:
        file.write(f"{link}\n")

print("链接已保存到 links.txt 文件中。")
