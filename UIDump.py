import getopt
import os
import sys
import time
import traceback

rootdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(rootdir)

from GlobalConfig import DUMP_INTERVAL, MONKEY_TIME, RECORD_OUTPUT_PATH, MONKEY_TIME_INTERVAL, LOG_OUTPUT_PATH
from lib.Logger import initLogger
from lib.RunStatus import RunStatus, isSuccess
from src.DeviceConnect import DeviceConnect
from src.Monkey import Monkey
from src.Timer import Timer


class UIDump:

    def __init__(self, argv):

        self.udid = ""
        self.pkgname = ""
        self.dumpInterval = DUMP_INTERVAL
        self.apkFilePath = ""
        self.monkeyMode = False
        self.monkeyTime = MONKEY_TIME
        self.recordOutPath = RECORD_OUTPUT_PATH
        self.device = None
        self.timer = None
        self.logger = None
        self.runStatus = RunStatus.SUCCESS

        self.__getConfig(argv)

        pass

    def __getConfig(self, argv):

        try:
            opts, args = getopt.getopt(argv, "p:f:m:o:d:",
                                       ["package=", "apkfile=", "monkeytime=", "output=", "device="])
        except getopt.GetoptError:
            self.__printUseMethod()
            sys.exit(2)

        for opt, arg in opts:
            if opt == '-h':
                self.__printUseMethod()
                sys.exit()
            elif opt in ("-p", "--package"):
                self.pkgname = arg
            elif opt in ("-f", "--apkfile"):
                self.apkFilePath = arg
            elif opt in ("-m", "--monkeytime"):
                self.monkeyTime = int(arg)
                self.monkeyMode = True
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

        if self.pkgname == "" or self.pkgname is None:
            print("package name is necessary")
            self.__printUseMethod()
            sys.exit(1)

        # 未指定设备取第一个
        if self.udid == "":
            print("no specified device!")
            self.udid = [line.split('\t')[0] for line in
                         os.popen("adb devices", 'r', 1).read().split('\n') if
                         len(line) != 0 and line.find('\tdevice') != -1][0]
            if self.udid == "":
                print("no available devices!")
                sys.exit(1)

                # 初始化Logger
        self.logger = initLogger(loggerName="UIDump_%s" % self.pkgname,
                                 outputPath=os.path.join(LOG_OUTPUT_PATH, "UIDump_%s.log" % self.pkgname),
                                 udid=self.udid)

        # 初始化 uiautomator
        try:
            self.device = DeviceConnect(self.logger, self.udid)
        except Exception as e:
            self.runStatus = RunStatus.UI2_INIT_ERR
            return

        # Monkey模式 设置计时器
        if self.monkeyMode:
            self.timer = Timer(logger=self.logger, duration=self.monkeyTime, device=self.device)

        # APK_FILE不为空，表示需要从指定路径安装app
        if self.apkFilePath is not "":
            self.runStatus = self.device.installApk(self.pkgname, self.apkFilePath)

        pass

    def __printUseMethod(self):
        print("UIDump.py -p <app-package-name> [-t] <dump-interval> "
              "[-f] <apk-file-path> [-m] <monkey-run-time> [-o] <output-path>")
        print("arguments : ")
        print("-p --package\tinput app is necessary, such as \"-p com.tencent.mm\"")
        print("-f --apkfile\tapk file path, if the app isn't installed, "
              "you can specify the apk file path, such as '/home/user/a.apk' or 'http://127.0.0.1:8000/user/a.apk")
        print("-m --monkeytime\t monkey run time, if it isn't specified, you can dump through manual operation")
        print("-o --output\t output path, default is ./output/record")

        pass

    def startUIDump(self):

        if not isSuccess(self.runStatus):
            self.device.uninstallApk(self.pkgname)
            return self.runStatus

        self.logger.info("start record mode, the package is %s and dump interval is %d"
                         % (self.pkgname, self.dumpInterval))

        timestamp = time.strftime('%Y%m%d%H%M', time.localtime())
        self.logger.info("log start at %s" % timestamp)

        try:
            self.runStatus = self.startRecord(timestamp)
        except Exception as e:
            traceback.print_exc()
            self.logger.error("unknown err in dump %s, Reason: %s" % (self.pkgname, e))
            self.runStatus = RunStatus.ERROR

        if self.apkFilePath is not "":
            self.device.uninstallApk(self.pkgname)

        timestamp = time.strftime('%Y%m%d%H%M', time.localtime())
        self.logger.info("log end at %s\r\n" % timestamp)

        return self.runStatus

    def startRecord(self, timestamp):

        if self.pkgname == "":
            self.logger.error("no input package name")
            return RunStatus.ERROR

        if self.pkgname not in self.device.getInstalledApps():
            self.logger.error("%s is not installed" % self.pkgname)
            return RunStatus.APK_INSTALL_ERR

        outputpath = os.path.join(self.recordOutPath, self.pkgname + "_" + timestamp)

        if not os.path.exists(outputpath):
            os.makedirs(outputpath)

        # 初始化frida
        # ch = CallerHook(self.pkgname, outputpath)
    
        time.sleep(1)
        
        # 设置回调事件
        try:
            # self.device.startWatchers()
            pass
        except Exception:
            import shutil
            shutil.rmtree(outputpath)
            self.logger.error("err in start watcher")
            return RunStatus.UI2_WATCHER_ERR

        if self.timer is None:
            # 没设置Timer, 人工跑APP还是用home键退出脚本
            stopcondition = self.device.getCurrentApp()
            while stopcondition is "":
                stopcondition = self.device.getCurrentApp()
            self.timer = Timer(stopcondition=stopcondition, device=self.device, logger=self.logger)

        self.device.pressHome()
        dumpcount = 1
        time.sleep(1)

        # 目前利用frida孵化进程有bug，用Monkey起
        self.runStatus = self.device.startApp(self.pkgname)
        if not isSuccess(self.runStatus):
            import shutil
            shutil.rmtree(outputpath)
            self.logger.error("err in start app")
            return self.runStatus

        # ch.start_hook(os.path.join("OneForAllHook", "_agent.js"), str(self.udid))
        time.sleep(5)  # 有时候app界面还没加载出来，等5s

        # 如果设置了MONKEY_TIME，启动monkey
        monkey = None
        if self.monkeyMode and self.device.getAppInstallStatus():
            monkey = Monkey(logger=self.logger, udid=self.udid, pkgname=self.pkgname,
                            timeInterval=MONKEY_TIME_INTERVAL, outdir=outputpath)
            self.runStatus = monkey.startMonkey()
        if not isSuccess(self.runStatus):
            import shutil
            shutil.rmtree(outputpath)
            self.logger.error("err in start monkey")
            return self.runStatus

        # 启动计时器
        starttime = self.timer.start()
        # 异常重启次数，有些app确实起不起来，最多重启3次
        errRestartCount = 0
        # 等待启动之后再轮询判断是否已经退出
        while True:
            if not self.device.isAppRun(self.pkgname):
                self.logger.info("app %s is not running " % self.pkgname)
                if monkey is not None:
                    execStatus, self.runStatus = monkey.stopMonkey()
                    if execStatus:
                        monkey = None
                    if not isSuccess(self.runStatus):
                        break
                # 如果app异常退出，且计时未结束重启app
                # getAppInstallStatus 避免当前app因为apk问题导致反复重启
                if self.monkeyMode and not self.timer.isFinish() and self.device.getAppInstallStatus() and errRestartCount < 3:
                    errRestartCount += 1
                    self.logger.warning("Abnormal termination in app running, restart, count = %d" % errRestartCount)
                    self.device.closeWatchers()

                    try:
                        self.device.startWatchers()
                    except Exception:
                        self.runStatus = RunStatus.UI2_WATCHER_ERR
                        break

                    self.runStatus = self.device.startApp(self.pkgname)
                    if not isSuccess(self.runStatus):
                        break

                    # ch.start_hook(os.path.join("OneForAllHook", "_agent.js"), str(self.udid))
                    time.sleep(5)
                    monkey = Monkey(logger=self.logger, udid=self.udid, pkgname=self.pkgname,
                                    timeInterval=MONKEY_TIME_INTERVAL, outdir=outputpath)
                    self.runStatus = monkey.startMonkey()
                    if not isSuccess(self.runStatus):
                        break

                    continue

                self.device.stopApp(self.pkgname)
                self.logger.info(self.pkgname + " is canceled, stop record, with restart count = %d" % errRestartCount)
                # ch.stop_hook()
                self.device.pressHome()
                break

            self.logger.info("dump %s UI" % str(dumpcount))
            self.runStatus = self.device.dumpUI(outputpath, dumpcount)
            if not isSuccess(self.runStatus):
                break
            dumpcount += 1
            time.sleep(self.dumpInterval)
            if self.timer.isFinish():
                if monkey is not None:
                    execStatus, self.runStatus = monkey.stopMonkey()
                    if execStatus:
                        monkey = None
                    if not isSuccess(self.runStatus):
                        break
                self.device.stopApp(self.pkgname)
                self.device.pressHome()
                break

        self.device.closeWatchers()
        time.sleep(5)
        
        if monkey is not None:
            _, self.runStatus = monkey.stopMonkey()

        if not self.device.getAppInstallStatus():
            import shutil
            shutil.rmtree(outputpath)
            self.logger.warning("err in apk, pass the case")
            return RunStatus.APK_INSTALL_ERR
        elif errRestartCount >= 3:
            import shutil
            shutil.rmtree(outputpath)
            self.logger.warning("app restart more than 3 times, pass the case")
            return RunStatus.APK_INSTALL_ERR
        elif not isSuccess(self.runStatus):
            import shutil
            shutil.rmtree(outputpath)
            self.logger.error("err in restart record")
            return self.runStatus
        else:
            self.device.saveLog(outputpath, starttime)
            self.logger.info("the output saved in " + outputpath)
        
        return self.runStatus.SUCCESS


if __name__ == "__main__":
    ud = UIDump(sys.argv[1:])
    ud.startUIDump()
