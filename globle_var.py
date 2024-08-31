'''全局变量区域（通常不需要改动）'''

from threading import Lock

# 用于存储并去重需要访问的页面链接
page_links = set()
lock_page_links = Lock()
# 通过对比哈希值实现对最终文本文件进行去重
page_hash = set()
lock_page_hash = Lock()
# 用于存储并去重已访问过的页面链接
searched_url = set()
lock_searched_url = Lock()

# 由于文件链接没有去重的需求，同时需要变动，所以使用list
file_links = []
lock_file_links = Lock()
# 变量结构：list[list[str(source_url),list[str(file_url)]]]

# 存储已经完成下载任务的页面链接
files_mask = set()
lock_files_mask = Lock()

# 记录文件路径与源url的映射关系，方便从网页文件直接查询到其所属的资源路径
file_mappping = {}
lock_file_mappping = Lock()
'''字典格式示例
{
	"http___www.hdu.edu.cn_761_list.htm": {
		"url": "http://www.hdu.edu.cn/761/list.htm",
		"src": ["./files/www.hdu.edu.cn/1.pdf", "./files/www.hdu.edu.cn/2.jpg"]
	}
}

{
	"http___www.hdu.edu.cn_762_list.htm": {
		"url": "http://www.hdu.edu.cn/762/list.htm",
		"src": ["./files/www.hdu.edu.cn/3.pdf", "./files/www.hdu.edu.cn/4.jpg"]
	}  
}
'''