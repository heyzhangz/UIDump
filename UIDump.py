import getopt
import os
import sys

#  Global config
import time

import ReranOpt
from GlobalConfig import RECORD_ROOT_PATH, REPLAY_ROOT_PATH

DUMP_INTERVAL = 1
PACKAGE_NAME = ""


def startUIDump(argv):
    global PACKAGE_NAME
    global DUMP_INTERVAL

    try:
        opts, args = getopt.getopt(argv, "p:t:r:", ["package=", "interval=", "replay="])
    except getopt.GetoptError:
        printUseMethod()
        sys.exit(2)

    recordmode = True
    replyfile = ""
    for opt, arg in opts:
        if opt == '-h':
            printUseMethod()
            sys.exit()
        elif opt in ("-p", "--package"):
            PACKAGE_NAME = arg
        elif opt in ("-t", "--interval"):
            DUMP_INTERVAL = int(arg)
        elif opt in ("-r", "--reply"):
            recordmode = False
            if not os.path.exists(arg):
                print("no such file " + arg)
                sys.exit(1)
            else:
                replyfile = arg
        else:
            print("err args : " + arg)
            printUseMethod()
            sys.exit(1)

    if PACKAGE_NAME == "":
        print("no package name")
        printUseMethod()
        sys.exit(1)

    if recordmode:
        print("start record mode, the package is \"" + PACKAGE_NAME + "\" and dump interval is " + str(DUMP_INTERVAL))
        recordOpt(PACKAGE_NAME, DUMP_INTERVAL)
    else:
        print("start replay mode, the package is \"" + PACKAGE_NAME + "\" and dump interval is " +
              str(DUMP_INTERVAL) + " with reply file " + replyfile)
        replayOpt(PACKAGE_NAME, DUMP_INTERVAL, replyfile)

    pass


def recordOpt(pacname="", interval=1, outputpath=""):

    if pacname == "":
        print("no package name")
        return

    from DeviceConnect import device
    timestamp = time.strftime('%Y%m%d%H%M', time.localtime())
    if outputpath == "":
        outputpath = RECORD_ROOT_PATH + pacname + "_" + timestamp + "\\"

    print("record the sequence of operations")
    device.startApp(pacname)
    ReranOpt.startRecord(outputpath)
    while True:
        if device.getCurrentPackage() != pacname:
            print(pacname + "is canceled, stop record")
            break

        time.sleep(interval)
    ReranOpt.endRecord(outputpath)

    time.sleep(1)
    print("replay and dump the UI")
    replayOpt(pacname, interval, outputpath + "replyscript.txt", outputpath)

    pass


def replayOpt(pacname="", interval=1, replyfile="", outputpath=""):

    if pacname == "":
        print("no package name")
        return

    from DeviceConnect import device
    timestamp = time.strftime('%Y%m%d%H%M', time.localtime())
    if outputpath == "":
        outputpath = REPLAY_ROOT_PATH + pacname + "_" + timestamp + "\\"
    dumpcount = 1

    device.startApp(pacname)
    time.sleep(1)  # 有时候app界面还没加载出来，等1s
    ReranOpt.startReplay(replyfile)
    while True:
        if device.getCurrentPackage() != pacname:
            print(pacname + "is canceled, stop replay")
            break
        device.dumpUI(outputpath, dumpcount)
        dumpcount += 1

        time.sleep(interval)

    pass


def printUseMethod():
    print("UIDump.py [-r] -p <app-package-name> -t <dump-interval> -f <reply-file>")
    print("arguments : ")
    print("-r --replay\treplay mode and need a replay script, such as \"-r ./replayscript\"")
    print("-p --package\tinput app, such as \"-p com.tencent.mm\"")
    print("-t --interval\tdump interval, default is 1s, \"-t 2\"")
    print()


if __name__ == "__main__":
    startUIDump(sys.argv[1:])
