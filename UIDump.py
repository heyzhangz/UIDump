import getopt
import os
import sys
import time
import traceback

from GlobalConfig import DUMP_INTERVAL, MONKEY_TIME, RECORD_OUTPUT_PATH, MONKEY_TIME_INTERVAL, LOG_OUTPUT_PATH
from OneForAllHook.hook_start import CallerHook
from lib.Common import deleteFile
from lib.Logger import initLogger
from src.DeviceConnect import DeviceConnect
from src.Monkey import Monkey
from src.Timer import Timer


class UIDump:

    def __init__(self, argv):

        self.udid = ""
        self.pkgname = ""
        self.dumpInterval = DUMP_INTERVAL
        self.apkFilePath = ""
        self.monkeyTime = MONKEY_TIME
        self.recordOutPath = RECORD_OUTPUT_PATH
        self.device = None
        self.timer = None
        self.logger = None

        self.__getConfig(argv)

        pass

    def __getConfig(self, argv):

        try:
            opts, args = getopt.getopt(argv, "p:t:f:m:o:d:",
                                       ["package=", "interval=", "apkfile=", "monkeytime=", "output=", "device="])
        except getopt.GetoptError:
            self.__printUseMethod()
            sys.exit(2)

        for opt, arg in opts:
            if opt == '-h':
                self.__printUseMethod()
                sys.exit()
            elif opt in ("-p", "--package"):
                self.pkgname = arg
            elif opt in ("-t", "--interval"):
                self.dumpInterval = int(arg)
            elif opt in ("-f", "--apkfile"):
                self.apkFilePath = arg
            elif opt in ("-m", "--monkeytime"):
                self.monkeyTime = int(arg)
            elif opt in ("-o", "--output"):
                self.recordOutPath = arg
                if not os.path.exists(self.recordOutPath):
                    os.makedirs(self.recordOutPath)
            elif opt in ("-d", "--device"):
                self.udid = arg
            else:
                print("err in args")
                self.__printUseMethod()
                sys.exit(1)

        if self.pkgname == "":
            print("package name is necessary")
            self.__printUseMethod()
            sys.exit(1)

        # 初始化Logger
        self.logger = initLogger(loggerName="UIDump_%s" % self.pkgname,
                                 outputPath=os.path.join(LOG_OUTPUT_PATH, "UIDump_%s.log" % self.pkgname))

        # 设置计时器
        if self.monkeyTime != 0:
            self.timer = Timer(logger=self.logger, duration=self.monkeyTime)

        if self.udid == "":
            self.udid = [line.split('\t')[0] for line in
                         os.popen("adb devices", 'r', 1).read().split('\n') if
                         len(line) != 0 and line.find('\tdevice') != -1][0]
            if self.udid == "":
                self.logger.error("no available devices")
                sys.exit(1)

        self.device = DeviceConnect(self.logger, self.udid)

        # APK_FILE不为空，表示需要从指定路径安装app
        if self.apkFilePath is not "":
            try:
                self.device.installApk(self.pkgname, self.apkFilePath)
            except Exception as e:
                self.logger.warning("err in install app %s from %s, Exception: %s", (self.pkgname, self.apkFilePath, e))
                traceback.print_exc()
                delFilePath = 'tmp_%s.apk' % self.pkgname
                try:
                    self.logger.info("delete file %s" % delFilePath)
                    deleteFile(delFilePath)
                except Exception as ee:
                    self.logger.warning("delete %s failed! %s" % (delFilePath, ee))
                    traceback.print_exc()
                return

        pass

    def __printUseMethod(self):
        print("UIDump.py -p <app-package-name> [-t] <dump-interval> "
              "[-f] <apk-file-path> [-m] <monkey-run-time> [-o] <output-path>")
        print("arguments : ")
        print("-p --package\tinput app is necessary, such as \"-p com.tencent.mm\"")
        print("-t --interval\tdump interval, default is 1s, \"-t 2\"")
        print("-f --apkfile\tapk file path, if the app isn't installed, "
              "you can specify the apk file path, such as '/home/user/a.apk' or 'http://127.0.0.1:8000/user/a.apk")
        print("-m --monkeytime\t monkey run time, if it isn't specified, you can dump through manual operation")
        print("-o --output\t output path, default is ./output/record")

        pass

    def startUIDump(self):

        self.logger.info("start record mode, the package is %s and dump interval is %d" % (self.pkgname, self.dumpInterval))

        self.startRecord()

        if self.apkFilePath is not "":
            self.device.uninstallApk(self.pkgname)

        pass

    def startRecord(self):

        if self.pkgname == "":
            self.logger.error("no input package name")
            return

        if self.pkgname not in self.device.getInstalledApps():
            self.logger.error("%s is not installed" % self.pkgname)
            return

        timestamp = time.strftime('%Y%m%d%H%M', time.localtime())
        outputpath = os.path.join(self.recordOutPath, self.pkgname + "_" + timestamp)

        self.logger.info("log start at %s" % timestamp)

        if not os.path.exists(outputpath):
            os.makedirs(outputpath)

        # 初始化frida
        # ch = CallerHook(self.pkgname, outputpath)
        # 设置回调事件
        self.device.startWatchers()

        if self.timer is None:
            # 没设置Timer, 人工跑APP还是用home键退出脚本
            stopcondition = self.device.getCurrentApp()
            while stopcondition is "":
                stopcondition = self.device.getCurrentApp()
            self.timer = Timer(stopcondition=stopcondition, device=self.device)

        self.device.pressHome()
        dumpcount = 1
        time.sleep(1)

        # 目前先利用frida孵化进程 有bug，用Monkey起
        self.device.startApp(self.pkgname)
        # ch.start_hook(os.path.join("OneForAllHook", "_agent.js"), str(self.udid))
        time.sleep(5)  # 有时候app界面还没加载出来，等5s

        # 如果设置了MONKEY_TIME，启动monkey
        monkey = None
        if self.monkeyTime != 0 and self.device.getAppInstallStatus():
            monkey = Monkey(logger=self.logger, udid=self.udid, pkgname=self.pkgname,
                            timeInterval=MONKEY_TIME_INTERVAL, outdir=outputpath)
            monkey.startMonkey()

        # 启动计时器
        self.timer.start()
        # 异常重启次数，有些app确实起不起来，最多重启3次
        errRestartCount = 0
        # 等待启动之后再轮询判断是否已经退出
        while True:
            if not self.device.isAppRun(self.pkgname):
                self.logger.info("app %s is not running " % self.pkgname)
                # 清一下白名单APP，防止对后续dump造成影响
                # device.stopApp()
                if monkey is not None:
                    monkey.stopMonkey()
                # 如果app异常退出，且计时未结束重启app
                # getAppInstallStatus 避免当前app因为apk问题导致反复重启
                if not self.timer.isFinish() and self.device.getAppInstallStatus() and errRestartCount < 3:
                    errRestartCount += 1
                    self.logger.warning("Abnormal termination in app running, restart, count = %d" % errRestartCount)
                    self.device.closeWatchers()
                    self.device.startWatchers()
                    self.device.startApp(self.pkgname)
                    # ch.start_hook(os.path.join("OneForAllHook", "_agent.js"), str(self.udid))
                    time.sleep(5)
                    monkey.startMonkey()
                    continue

                self.device.stopApp(self.pkgname)
                self.logger.info(self.pkgname + " is canceled, stop record, with restart count = %d" % errRestartCount)
                # ch.stop_hook()
                self.device.pressHome()
                break
            self.logger.info("dump %s UI" % str(dumpcount))
            self.device.dumpUI(outputpath, dumpcount)
            dumpcount += 1
            time.sleep(self.dumpInterval)
            if self.timer.isFinish():
                if monkey is not None:
                    monkey.stopMonkey()
                self.device.stopApp(self.pkgname)
                self.device.pressHome()

        self.device.closeWatchers()
        time.sleep(5)

        if not self.device.getAppInstallStatus():
            import shutil
            shutil.rmtree(outputpath)
            self.logger.warning("err in apk, pass the case")
        else:
            self.logger.info("the output saved in " + outputpath)

        self.logger.info("log end\r\n\r\n")

        pass


if __name__ == "__main__":
    ud = UIDump(sys.argv[1:])
    ud.startUIDump()
