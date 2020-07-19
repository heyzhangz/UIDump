import logging
import os

BASE_PATH = os.path.dirname(__file__)
DEPENDENCY_PATH = os.path.join(BASE_PATH, 'dependency')
RECORD_OUTPUT_PATH = os.path.join(BASE_PATH, "output", "record")
LOG_OUTPUT_PATH = os.path.join(BASE_PATH, "output", "log")

# 框架配置
DUMP_INTERVAL = 1
UI_WATCHER_TIME_INTERVAL = 1
MONKEY_TIME = 3600

# 多任务模式配置
DEVICE_LIST = []
APP_LIST_PATH = os.path.join(BASE_PATH, "category_top_bak.json")

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
