
from concurrent.futures import ThreadPoolExecutor, as_completed
from logger_setup import logger
import globle_var as gv
import config
from file_operator import create_config_files, clear_history, searched_url_file, page_hash_file, file_link_file, page_link_file, files_mask_file, files_mapping_file, error_url_file
from get_resource import crawl_recursive, create_driver, download_file, wash_url

from tqdm import tqdm





if __name__ == "__main__":

    clear_history()
    create_config_files()
    gv.page_hash = page_hash_file.read()
    gv.searched_url = searched_url_file.read()
    gv.page_links = page_link_file.read()
    gv.file_links = file_link_file.read()
    gv.files_mask = files_mask_file.read()


    driver = None
    if False: # 控制是否使用Selenium+EdgeDriver爬取
        # 启动Selenium WebDriver
        logger.info("正在启动Selenium WebDriver...")
        driver = create_driver()

    
    logger.info("开始爬取网页...")
    # 从首页开始爬取
    if not gv.page_links:
        logger.info("未检测到历史进度，将从头开始爬取网页")
        gv.page_links.add(config.start_url)
    else:
        # 如果双方相等，说明上次爬取已经完成
        if len(gv.page_links) == len(gv.searched_url):
            logger.info("网页已在上次爬取完成，后续将开始下载文件")
        else:
            logger.info("检测到爬取历史，继续上次未完成的爬取")

    
    # 统计已爬取链接个数
    page_cnt_ok = len(gv.searched_url)
    # 统计所有链接个数
    page_cnt_all = len(gv.page_links)
    # 统计剩余链接个数
    gv.page_links -= gv.searched_url
    page_cnt_remain = len(gv.page_links)
    logger.info(f"当前总页面数: {page_cnt_all}，已经爬取的页面数: {page_cnt_ok}，剩余页面数: {page_cnt_remain}")

    # 创建线程池
    with ThreadPoolExecutor(max_workers=config.page_max_workers) as executor:  # 根据需求调整max_workers
        # 爬取
        with tqdm(total=page_cnt_all) as pbar:
            pbar.n = page_cnt_ok
            futures = []
            while True:
                with gv.lock_page_links:
                    if not gv.page_links:
                        break
                    # 取出一批链接
                    links_batch = [gv.page_links.pop() for _ in range(min(config.page_max_workers, len(gv.page_links)))]

                # 提交任务到线程池
                for link in links_batch:
                    future = executor.submit(crawl_recursive, link, driver)
                    futures.append(future)

                # 处理完成的任务
                for future in as_completed(futures):
                    pbar.total += future.result()
                    pbar.update(1)
                    pbar.refresh()

                # 清空 futures 列表以准备下一批任务
                futures.clear()

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
    if not gv.files_mask:
        logger.info("未检测到历史进度，将从头开始下载文件")
    else:
        logger.info("检测到下载历史，继续上次未完成的下载")



    # 统计所有的文件个数
    files_cnt_all = sum([len(links[1]) for links in gv.file_links])
    # 剩余文件个数
    gv.file_links = [links for links in gv.file_links if links[0] not in gv.files_mask]
    files_cnt_remain = sum([len(links[1]) for links in gv.file_links])
    # 已下载文件个数
    files_cnt_ok = files_cnt_all - files_cnt_remain
    logger.info(f"当前总文件数: {files_cnt_all}，已经下载的文件数: {files_cnt_ok}，剩余文件数: {files_cnt_remain}")

    # 下载
    with tqdm(total=files_cnt_all) as pbar:
        pbar.n = files_cnt_ok
        while gv.file_links:
            # 取出一个链接
            url, links = gv.file_links[-1]
            logger.info(f"[下载文件] 所属页面：{url}")

            # 下载此页面中的文件
            sources = []
            for link in links:
                file_path = download_file(link)
                sources.append(file_path)

            # 将当前URL添加到已下载列表
            gv.files_mask.add(url)
            files_mask_file.save_line(url)
            # 记录文件映射
            file_mappping = {wash_url(url): {"url": url, "src": sources}}
            files_mapping_file.save_line(file_mappping)
            # 从待下载列表中删除
            gv.file_links.pop()
            # 更新进度条
            files_cnt_ok += len(links)
            pbar.n = files_cnt_ok
            pbar.refresh()
            
    logger.info("全部文件下载完成！")