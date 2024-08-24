'''基础配置区域'''

# 仅访问此域名范围的url
domain = "xxx.edu.cn"

# 以此url作为起始页面，开始迭代式爬取
start_url = "https://xxx.edu.cn/"

# 保存时是否转换为md格式（设为False则只保存原始的html文件，设为True则同时保存html和md文件）
trans_md = True

'''进阶配置区域'''

# 请求头设置：如果你需要添加cookie等信息用来访问需要登录的网页内容，可以在此处添加
request_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

# URL排除项：url中包含以下字符串的将被排除。如果你想下载新闻、登录、注册等页面，可以在此处删除掉对应的字符串
exclusions = ["news","login","register","webvpn"]

# 注意，以下3个list选项都是在转换为md格式时才会生效，HTML文件只会保存原始的HTML内容
# 精确匹配：包含以下id或class的标签元素将被删除
tags = ["footer", "sidebar","navigation-bar","banner","foot-bar","wrapper header",
			   "t-top","c header","f-nav c","wrapper footer","wrapper nav wp-navi","nav",
			   "navbar uk-navbar-transparent uk-sticky","head","foot","header clearfix",
			   "footer clearfix","nav_min showhead","ind_navigationbg","menu-ul","erjicaidan l",
               "logo_menu_bj"
			   ]

# 模糊匹配：在class或id中包含以下字符串的标签元素将被删除
tags_fuzzy = ["foot","head"]

# 去除超链接：在删除包含超链接或相关内容的标签。如果你不想去除超链接，可以将此项设置为空列表
hyperlinked_tags = ['a', 'img', 'iframe', 'area']

# 文本文件判定：以下后缀名结尾的链接将被下载
text_tails = ('.pdf', '.docx', '.txt', '.md', '.csv', 
                '.xls', '.xlsx', '.doc','.rtf')

# 文件判定：以下后缀名结尾的链接将不会被视作页面链接
file_tails = ('.pdf', '.docx', '.txt', '.jpg', '.png', '.gif', '.jpeg', '.zip', '.rar',
				'.7z', '.exe', '.apk', '.mp3', '.mp4', '.avi', '.flv', '.mov', '.wmv',
				'.wma', '.wav', '.flac', '.ogg', '.m4a', '.m4v', '.mkv', '.webm', '.swf', 
				'.iso', '.torrent', '.magnet', '.csv', '.xls', '.xlsx', '.doc', '.ppt', 
				'.pptx', '.odt', '.ods', '.odp', '.rtf', '.epub', '.mobi', '.azw', 
				'.azw3', '.djvu', '.fb2', '.ps', '.eps', '.ai', '.svg', '.webp', '.heic', 
				'.heif', '.cr2', '.nef', '.orf', '.arw', '.rw2', '.dng', '.raf', '.pef', 
				'.srf', '.sr2', '.x3f', '.erf', '.mrw', '.nrw', '.rwl', '.raw', '.crw', 
				'.cr3', '.kdc', '.dcr', '.tif', '.tiff', '.bmp', '.webp')

'''全局变量区域（通常不需要改动）'''

from urllib3.exceptions import InsecureRequestWarning
import warnings
# 禁用不安全请求的警告
warnings.simplefilter('ignore', InsecureRequestWarning)

# 用于存储并去重需要访问的页面链接
page_links = set()
# 通过对比哈希值实现对最终文本文件进行去重
page_hash = set()
# 用于存储并去重已访问过的页面链接
searched_url = set()

# 由于文件链接没有去重的需求，同时需要变动，所以使用list
file_links = []	
# 变量结构：list[list[str(source_url),list[str(file_url)]]]

# 存储已经完成下载任务的页面链接
files_mask = set()

# 记录文件路径与源url的映射关系，方便从网页文件直接查询到其所属的资源路径
file_mappping = {}
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