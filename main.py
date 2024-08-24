import jsonlines
from logger_setup import logger
import globle_var as gl

from file_operator import create_config_files, read_page_hash, read_searched_url, read_file_links, read_page_links, clear_history, saveline_page_link, saveline_file_link, saveline_files_mask, read_files_mask, read_page_links, saveline_files_mapping, saveline_searched_url
from get_resource import crawl_recursive, create_driver, download_file, wash_url, stable_hash

from tqdm import tqdm
import json




if __name__ == "__main__":

    #clear_history()
    create_config_files()
    gl.page_hash = read_page_hash()
    gl.searched_url = read_searched_url()
    gl.file_links = read_file_links()
    gl.page_links = read_page_links()
    gl.files_mask = read_files_mask()


    driver = None
    if False: # 控制是否使用Selenium+EdgeDriver爬取
        # 启动Selenium WebDriver
        logger.info("正在启动Selenium WebDriver...")
        driver = create_driver()

    
    logger.info("开始爬取网页...")
    # 从首页开始爬取
    if not gl.page_links:
        logger.info("未检测到历史进度，将从头开始爬取网页")
        gl.page_links.add(gl.start_url)
    else:
        # 如果双方相等，说明上次爬取已经完成
        if len(gl.page_links) == len(gl.searched_url):
            logger.info("网页已在上次爬取完成，后续将开始下载文件")
        else:
            logger.info("检测到爬取历史，继续上次未完成的爬取")

    
    # 统计已爬取链接个数
    page_cnt_ok = len(gl.searched_url)
    # 统计所有链接个数
    page_cnt_all = len(gl.page_links)
    # 统计剩余链接个数
    gl.page_links -= gl.searched_url
    page_cnt_remain = len(gl.page_links)

    logger.info(f"当前总页面数: {page_cnt_all}，已经爬取的页面数: {page_cnt_ok}，剩余页面数: {page_cnt_remain}")

    # 爬取
    with tqdm(total=page_cnt_all) as pbar:
        pbar.n = page_cnt_ok
        while gl.page_links:
            link = next(iter(gl.page_links))    # 取出一个链接

            # 爬取页面
            rt = crawl_recursive(link, driver)
            if rt is not None:
                page_links, file_links = rt
                # 将新链接加入待爬取列表
                if page_links:
                    new_links = page_links - gl.searched_url
                    if new_links:
                        ori_num = len(gl.page_links)
                        gl.page_links.update(new_links)    # 将新链接加进待爬取列表（set自动去重）
                        saveline_page_link(new_links)
                        pbar.total += len(gl.page_links) - ori_num  # 重新设置 total 值   
                # 将新文件链接加入待下载列表            
                if file_links[1]:
                    saveline_file_link(file_links)
                    gl.file_links.append(file_links)       # 将新文件链接添加到待下载列表

            # 将当前URL添加到已爬取列表
            if link not in gl.searched_url:
                gl.searched_url.add(link)
                saveline_searched_url(link)
            # 从待爬取列表中删除
            gl.page_links.remove(link)

            # 更新进度条
            pbar.update(1)
            pbar.refresh()

    logger.info("全部网页爬取完成！")  


    file_mappping = {}
    '''字典格式示例
    {
        "http___www.hdu.edu.cn_761_list.htm": {
            "url": "http://www.hdu.edu.cn/761/list.htm",
            "src": ["./files/www.hdu.edu.cn/1.pdf", "./files/www.hdu.edu.cn/2.jpg"]
        },
        "http___www.hdu.edu.cn_762_list.htm": {
            "url": "http://www.hdu.edu.cn/762/list.htm",
            "src": ["./files/www.hdu.edu.cn/3.pdf", "./files/www.hdu.edu.cn/4.jpg"]
        }  
    }
    实现从网页文件直接查询到其所属的资源路径
    '''
    logger.info("开始下载文件并映射...")
    if not gl.files_mask:
        logger.info("未检测到历史进度，将从头开始下载文件")
    else:
        logger.info("检测到下载历史，继续上次未完成的下载")



    # 统计所有的文件个数
    files_cnt_all = sum([len(links[1]) for links in gl.file_links])
    # 剩余文件个数
    gl.file_links = [links for links in gl.file_links if links[0] not in gl.files_mask]
    files_cnt_remain = sum([len(links[1]) for links in gl.file_links])
    # 已下载文件个数
    files_cnt_ok = files_cnt_all - files_cnt_remain
    logger.info(f"当前总文件数: {files_cnt_all}，已经下载的文件数: {files_cnt_ok}，剩余文件数: {files_cnt_remain}")

    # 下载
    with tqdm(total=files_cnt_all) as pbar:
        pbar.n = files_cnt_ok
        while gl.file_links:
            # 取出一个链接
            url, links = gl.file_links[-1]
            logger.info(f"[下载文件] 所属页面：{url}")

            # 下载此页面中的文件
            sources = []
            for link in links:
                file_path = download_file(link)
                sources.append(file_path)

            # 将当前URL添加到已下载列表
            gl.files_mask.add(url)
            saveline_files_mask(url)
            # 记录文件映射
            file_mappping = {wash_url(url): {"url": url, "src": sources}}
            saveline_files_mapping(file_mappping)
            # 从待下载列表中删除
            gl.file_links.pop()
            # 更新进度条
            files_cnt_ok += len(links)
            pbar.n = files_cnt_ok
            pbar.refresh()
    logger.info("全部文件下载完成！")