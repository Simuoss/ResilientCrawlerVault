# logger_setup.py
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os

# 创建日志目录（如果不存在）
log_dir = './logs'
os.makedirs(log_dir, exist_ok=True)

# 创建日志记录器
logger = logging.getLogger('app_logger')
logger.setLevel(logging.DEBUG)  # 设置日志记录器的级别为 DEBUG

# 防止重复添加处理器
if not logger.hasHandlers():
    # 创建控制台处理器，级别为 ERROR
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    max_file_size = 1 * 1024 * 1024  # 1MB

    def get_log_filename():
        """生成带时间戳的日志文件名"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(log_dir, f'app_{timestamp}.log')

    def current_log_file(max_file_size=4*1024*1024):
        """查找最新的、大小小于4MB的日志文件"""
        log_files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.startswith('app_') and f.endswith('.log')]

        latest_file = None
        latest_time = None
        
        for file in log_files:
            if os.path.getsize(file) < max_file_size:
                file_time = datetime.fromtimestamp(os.path.getctime(file))
                if latest_time is None or file_time > latest_time:
                    latest_time = file_time
                    latest_file = file

        if latest_file is None:
            latest_file = get_log_filename()
        print(f'latest_file: {latest_file}')
        return latest_file

    # 创建文件处理器，初始文件名带有时间戳
    initial_log_file = current_log_file(max_file_size)
    file_handler = RotatingFileHandler(
        initial_log_file,
        #maxBytes=1*1024*1024,  # 4MB
        backupCount=100,         # 保留最近 5 个日志文件
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
