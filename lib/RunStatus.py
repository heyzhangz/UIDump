from enum import Enum, unique


@unique
class RunStatus(Enum):
    SUCCESS = 0

    ERROR = 999  # 其它异常

    # > 0 表示需要跳过的case
    # APP安装异常
    FILE_NOT_FIND = 1  # apk文件路径不存在
    APK_INSTALL_ERR = 2  # 安装失败，命令行执行返回值不为0、闪退、apk错误

    # < 0 表示环境异常的case, 在多任务模式下，该case要返回加入任务队列
    # APP 安装异常
    DOWNLOAD_ERR = -1  # 文件下载失败
    CMD_EXEC_ERR = -2  # adb 命令执行失败

    # uiautomator2 异常
    UI2_INIT_ERR = -11  # ui2 初始化异常
    UI2_WATCHER_ERR = -12  # ui2 watcher异常
    UI2_ERROR = -13  # ui2 其它异常

    # monkey 异常
    MONKEY_ERR = -21

    pass


def isSuccess(status: RunStatus) -> bool:
    if status is RunStatus.SUCCESS:
        return True

    return False


def isNeedContinue(status: RunStatus) -> bool:
    if status.value < 0:
        return True

    return False


def isNeedRestart(status: RunStatus) -> bool:
    if status.value < -10:
        return True

    return False
