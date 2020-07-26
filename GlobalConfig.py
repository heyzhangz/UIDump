import logging
import os

# 路径peizhi
BASE_PATH = os.path.dirname(__file__)
DEPENDENCY_PATH = os.path.join(BASE_PATH, 'dependency')  # 依赖文件路径
RECORD_OUTPUT_PATH = os.path.join(BASE_PATH, "output", "record")  # dump结果路径
LOG_OUTPUT_PATH = os.path.join(BASE_PATH, "output", "log")  # 日志路径

# 框架配置
DUMP_INTERVAL = 1  # dump时间间隔
UI_WATCHER_TIME_INTERVAL = 1  # UI watcher 监控分析间隔

# 多任务模式配置
MONKEY_TIME = 36000  # monkey运行时间，毫秒（该参数只影响多任务模式）
DEVICE_LIST = [
    'emulator-5554',
    'emulator-5556',
    'emulator-5558',
    'emulator-5560'
]  # 可选设备列表，[]或None表示使用全部在线设备
APP_LIST_PATH = os.path.join(BASE_PATH, "category_top_bak.json")  # app list 文件路径（TODO 注意Multi-UIDump.py文件读取格式可能也要改）

# 信息收集模块配置
SCREENSHOT_FILE_NAME = "screenshot.jpg"
LAYOUT_FILE_NAME = "layout.xml"

# Monkey配置
MONKEY_WHITE_LIST_NAME = "monkey_pkg_whitelist.txt"
MONKEY_WHITE_LIST_PATH = os.path.join(DEPENDENCY_PATH, MONKEY_WHITE_LIST_NAME)
MONKEY_TIME_INTERVAL = 800

# log配置
MONKEY_LOG_NAME = "monkey_log.log"
LOG_LEVEL = logging.DEBUG
