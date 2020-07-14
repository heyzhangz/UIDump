import getopt
import os
import sys
import time
import traceback

from MonkeyOpt import MonkeyOpt
from OneForAllHook.hook_start import CallerHook
from Timer import Timer
from Logger import logger

DUMP_INTERVAL = 1
PACKAGE_NAME = ""
APK_FILE = ""
MONKEY_TIME = 0
RECORD_ROOT_PATH = os.path.join(".", "output", "record")


def startUIDump(argv):
    global PACKAGE_NAME, APK_FILE, MONKEY_TIME, RECORD_ROOT_PATH
    global DUMP_INTERVAL

    try:
        opts, args = getopt.getopt(argv, "p:t:f:m:o:",
                                   ["package=", "interval=", "apkfile=", "monkeytime=", "output="])
    except getopt.GetoptError:
        printUseMethod()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            printUseMethod()
            sys.exit()
        elif opt in ("-p", "--package"):
            PACKAGE_NAME = arg
        elif opt in ("-t", "--interval"):
            DUMP_INTERVAL = int(arg)
        elif opt in ("-f", "--apkfile"):
            APK_FILE = arg
        elif opt in ("-m", "--monkeytime"):
            MONKEY_TIME = int(arg)
        elif opt in ("-o", "--output"):
            RECORD_ROOT_PATH = arg
            if not os.path.exists(RECORD_ROOT_PATH):
                os.makedirs(RECORD_ROOT_PATH)
        else:
            logger.error("err in args")
            printUseMethod()
            sys.exit(1)

    if PACKAGE_NAME == "":
        logger.error("package name is necessary")
        printUseMethod()
        sys.exit(1)

    logger.info("start record mode, the package is %s and dump interval is %d" % (PACKAGE_NAME, DUMP_INTERVAL))
    from DeviceConnect import device
    # APK_FILE不为空，表示需要从指定路径安装app
    if APK_FILE is not "":
        try:
            status = device.installApk(PACKAGE_NAME, APK_FILE)
            if not status:
                logger.warning("err in install app %s from %s" % (PACKAGE_NAME, APK_FILE))
                device.deleteInstallFile()
                return
        except Exception as e:
            logger.warning("err in install app %s from %s, Exception: %s", (PACKAGE_NAME, APK_FILE, e))
            traceback.print_exc()
            device.deleteInstallFile()
            return

    recordOpt(PACKAGE_NAME, DUMP_INTERVAL)

    if APK_FILE is not "":
        device.uninstallApk(PACKAGE_NAME)

    pass


def recordOpt(pkgname="", interval=1, outputpath=""):
    if pkgname == "":
        logger.error("no input package name")
        return

    from DeviceConnect import device
    timestamp = time.strftime('%Y%m%d%H%M', time.localtime())
    if outputpath == "":
        outputpath = os.path.join(RECORD_ROOT_PATH, pkgname + "_" + timestamp)

    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

    # 初始化frida
    ch = CallerHook(pkgname, outputpath)
    # 设置回调事件
    device.startWatchers()
    # 设置计时器
    if MONKEY_TIME != 0:
        timer = Timer(duration=MONKEY_TIME)
    else:
        # 人工跑APP还是用home键退出脚本
        stopcondition = device.getCurrentApp()
        while stopcondition is "":
            stopcondition = device.getCurrentApp()
        timer = Timer(stopcondition=stopcondition)

    device.pressHome()
    dumpcount = 1
    time.sleep(1)

    # 目前先利用frida孵化进程
    ch.run_and_start_hook(os.path.join("OneForAllHook", "_agent.js"))
    time.sleep(5)  # 有时候app界面还没加载出来，等5s

    # 如果设置了MONKEY_TIME，启动monkey
    monkey = None
    if MONKEY_TIME != 0 and device.getAppInstallStatus():
        monkey = MonkeyOpt(pkgname=pkgname, timeinterval=800)
        monkey.startMonkey()

    # 启动计时器
    timer.start()
    # 异常重启次数，有些app确实起不起来，最多重启3次
    err_restart_count = 0
    # 等待启动之后再轮询判断是否已经退出
    while True:
        if not device.isAppRun(pkgname):

            # 清一下白名单APP，防止对后续dump造成影响
            # device.stopApp()
            if monkey is not None:
                monkey.stopMonkey()
            # 如果app异常退出，且计时未结束重启app
            # getAppInstallStatus 避免当前app因为apk问题导致反复重启
            if not timer.isFinish() and device.getAppInstallStatus() and err_restart_count < 3:
                err_restart_count += 1
                logger.warning("Abnormal termination in app running, restart, count = %d" % err_restart_count)
                device.closeWatchers()
                device.startWatchers()
                ch.run_and_start_hook(os.path.join("OneForAllHook", "_agent.js"))
                time.sleep(5)
                monkey.startMonkey()
                continue

            device.stopApp(pkgname)
            logger.info(pkgname + " is canceled, stop record, with restart count = %d" % err_restart_count)
            ch.stop_hook()
            device.pressHome()
            break
        logger.info("dump %s UI" % str(dumpcount))
        device.dumpUI(outputpath, dumpcount)
        dumpcount += 1
        time.sleep(interval)
        if timer.isFinish():
            if monkey is not None:
                monkey.stopMonkey()
            device.stopApp(pkgname)
            device.pressHome()

    device.closeWatchers()
    time.sleep(5)

    if not device.getAppInstallStatus():
        import shutil
        shutil.rmtree(outputpath)
        logger.warning("err in apk, pass the case")
    else:
        logger.info("the output saved in " + outputpath)

    pass


def printUseMethod():
    print("UIDump.py -p <app-package-name> [-t] <dump-interval> "
          "[-f] <apk-file-path> [-m] <monkey-run-time> [-o] <output-path>")
    print("arguments : ")
    print("-p --package\tinput app is necessary, such as \"-p com.tencent.mm\"")
    print("-t --interval\tdump interval, default is 1s, \"-t 2\"")
    print("-f --apkfile\tapk file path, if the app isn't installed, "
          "you can specify the apk file path, such as '/home/user/a.apk' or 'http://127.0.0.1:8000/user/a.apk")
    print("-m --monkeytime\t monkey run time, if it isn't specified, you can dump through manual operation")
    print("-o --output\t output path, default is ./output/record")


if __name__ == "__main__":
    startUIDump(sys.argv[1:])
