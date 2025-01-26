import os
import logging

# 定义日志文件路径
log_file = os.path.dirname(os.path.realpath(__file__)) + "/logs/app.log"

# 检查并加载自定义配置
file_path = os.path.dirname(os.path.realpath(__file__)) + "/config/logging.ini"
if os.path.exists(file_path):
    import logging.config

    logging.config.fileConfig(file_path)
    log = logging.getLogger("AutoMihoyoBBS")
else:
    # 设置日志格式和输出
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
        handlers=[
            logging.StreamHandler(),  # 输出到控制台
            logging.FileHandler(log_file, encoding="utf-8")  # 输出到文件
        ]
    )
    log = logging

# 获取httpx的日志记录器，并将其级别设置为CRITICAL，让日志不再输出httpx的相关日志
httpx_log = logging.getLogger("httpx")
httpx_log.setLevel(logging.CRITICAL)

# 示例日志
log.info("Logging is successfully configured!")