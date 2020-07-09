import getopt
import os
import signal
import sys

#  Global config
import time

import frida

import ReranOpt
import GlobalConfig
from MonkeyOpt import MonkeyBase
from OneForAllHook.hook_start import CallerHook

DUMP_INTERVAL = 1
PACKAGE_NAME = ""
APKFILE = ""
MONKEY_TIME = 0
RECORD_ROOT_PATH = GlobalConfig.RECORD_ROOT_PATH


def startUIDump(argv):
    global PACKAGE_NAME, APKFILE, MONKEY_TIME, RECORD_ROOT_PATH
    global DUMP_INTERVAL

    try:
        opts, args = getopt.getopt(argv, "p:t:r:f:m:o:",
                                   ["package=", "interval=", "replay=", "apkfile=", "monkeytime=", "output="])
    except getopt.GetoptError:
        printUseMethod()
        sys.exit(2)

    recordmode = True
    replayfile = ""
    for opt, arg in opts:
        if opt == '-h':
            printUseMethod()
            sys.exit()
        elif opt in ("-p", "--package"):
            PACKAGE_NAME = arg
        elif opt in ("-t", "--interval"):
            DUMP_INTERVAL = int(arg)
        elif opt in ("-r", "--replay"):
            recordmode = False
            if not os.path.exists(arg):
                print("no such file " + arg)
                sys.exit(1)
            else:
                replayfile = arg
        elif opt in ("-f", "--apkfile"):
            if not arg.startswith("http://"):
                print("file url error! " + arg)
            APKFILE = arg
        elif opt in ("-m", "--monkeytime"):
            MONKEY_TIME = int(arg)
        elif opt in ("-o", "--output"):
            RECORD_ROOT_PATH = arg
            if not os.path.exists(RECORD_ROOT_PATH):
                os.makedirs(RECORD_ROOT_PATH)
        else:
            print("err args : " + arg)
            printUseMethod()
            sys.exit(1)

    if PACKAGE_NAME == "":
        print("[Error](UIDump) no package name")
        printUseMethod()
        sys.exit(1)

    if recordmode:
        print("[Info](UIDump) start record mode, the package is \"" + PACKAGE_NAME +
              "\" and dump interval is " + str(DUMP_INTERVAL))
        from DeviceConnect import device
        if APKFILE is not "":
            device.installApk(APKFILE)
        recordOpt(PACKAGE_NAME, DUMP_INTERVAL)
        if APKFILE is not "":
            device.uninstallApk(PACKAGE_NAME)
    else:
        print("[Info](UIDump) start replay mode, the package is \"" + PACKAGE_NAME + "\" and dump interval is " +
              str(DUMP_INTERVAL) + " with replay file " + replayfile)
        # replayOpt(PACKAGE_NAME, DUMP_INTERVAL, replayfile)
        print("[Info](UIDump) replay mode is abandoned temporarily")

    pass


# def recordOpt(pacname="", interval=1, outputpath=""):
#     if pacname == "":
#         print("no package name")
#         return
#
#     from DeviceConnect import device
#     timestamp = time.strftime('%Y%m%d%H%M', time.localtime())
#     if outputpath == "":
#         outputpath = RECORD_ROOT_PATH + pacname + "_" + timestamp + os.sep
#
#     print("record the sequence of operations")
#
#     # 先摁一下home键 记录一下主界面状态，用于判断退出程序
#     device.pressHome()
#     stopcondition = device.getCurrentApp()
#
#     device.startApp(pacname)
#     # 等待启动之后再轮询判断是否已经退出
#     time.sleep(1)
#     geteventpid = ReranOpt.startRecord(outputpath, device.getDeviceModel())
#     while True:
#         nowapp = device.getCurrentApp()
#         if nowapp == stopcondition:
#             device.stopApp(pacname)
#             print("package change to " + nowapp['package'])
#             print(pacname + "is canceled, stop record")
#             break
#
#         time.sleep(interval)
#     ReranOpt.endRecord(outputpath, geteventpid)
#
#     time.sleep(5)
#     print("replay and dump the UI")
#     replayOpt(pacname, interval, outputpath + "replayscript.txt", outputpath)
#
#     pass

def recordOpt(pacname="", interval=1, outputpath=""):
    if pacname == "":
        print("[Error](UIDump) no package name")
        return

    from DeviceConnect import device
    timestamp = time.strftime('%Y%m%d%H%M', time.localtime())
    if outputpath == "":
        # outputpath = RECORD_ROOT_PATH + pacname + "_" + timestamp + os.sep
        outputpath = os.path.join(RECORD_ROOT_PATH, pacname + "_" + timestamp)

    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

    ch = CallerHook(pacname, outputpath)
    dumpcount = 1

    # 设置回调事件
    device.startWatchers()
    # 先摁一下home键 记录一下主界面状态，用于判断退出程序
    device.pressHome()
    stopcondition = device.getCurrentApp()
    while stopcondition is "":
        stopcondition = device.getCurrentApp()

    # 先加载frida
    ch.run_and_start_hook(os.path.join("OneForAllHook", "_agent.js"))
    time.sleep(5)  # 有时候app界面还没加载出来，等1s
    monkey = None
    if MONKEY_TIME != 0:
        monkey = MonkeyBase(pacname=pacname, exectime=MONKEY_TIME, timeinterval=800)
        monkey.startMonkey()
    # 等待启动之后再轮询判断是否已经退出
    while True:
        nowapp = device.getCurrentApp()
        if nowapp is not "" and nowapp == stopcondition:
            device.stopApp(pacname)
            print("[Info](UIDump) package change to " + nowapp['package'])
            print("[Info](UIDump)" + pacname + "is canceled, stop record")
            print("[Info](UIDump) stop hook")
            ch.stop_hook()
            # 防止异常退出，比如错误安装，monkey还没关
            if monkey is not None:
                monkey.stopMonkey()
                device.pressHome()
            break
        print("[Info](UIDump) dump " + str(dumpcount) + "UI")
        device.dumpUI(outputpath, dumpcount)
        dumpcount += 1
        time.sleep(interval)
        if monkey is not None and monkey.isFinish():
            monkey.stopMonkey()
            device.pressHome()

    time.sleep(5)
    device.closeWatchers()
    print("[Info](UIDump) the output saved in " + outputpath)

    pass


# def replayOpt(pacname="", interval=1, replayfile="", outputpath=""):
#     if pacname == "":
#         print("no package name")
#         return
#
#     from DeviceConnect import device
#     timestamp = time.strftime('%Y%m%d%H%M', time.localtime())
#     if outputpath == "":
#         outputpath = REPLAY_ROOT_PATH + pacname + "_" + timestamp + os.sep
#     dumpcount = 1
#
#     device.pressHome()
#     stopcondition = device.getCurrentApp()
#     device.startApp(pacname)
#     time.sleep(1)
#     startHookAPI(pacname)
#     time.sleep(10)  # 有时候app界面还没加载出来，等1s
#     # 需要处理splash广告。。得多等一会儿
#     ReranOpt.startReplay(replayfile)
#     while True:
#         nowapp = device.getCurrentApp()
#         if nowapp == stopcondition:
#             device.stopApp(pacname)
#             print("package change to " + nowapp['package'])
#             print(pacname + "is canceled, stop replay")
#             break
#         device.dumpUI(outputpath, dumpcount)
#         dumpcount += 1
#
#         time.sleep(interval)
#
#     print("the output saved in " + outputpath)
#
#     pass

def printUseMethod():
    print("UIDump.py [-r] -p <app-package-name> -t <dump-interval> -f <replay-file>")
    print("arguments : ")
    print("-r --replay\treplay mode and need a replay script, such as \"-r ./replayscript\"")
    print("-p --package\tinput app, such as \"-p com.tencent.mm\"")
    print("-t --interval\tdump interval, default is 1s, \"-t 2\"")
    print()


if __name__ == "__main__":
    startUIDump(sys.argv[1:])
