import os
import subprocess
import time
import urllib.request

import uiautomator2

from GlobalConfig import SCREENSHOT_FILE_NAME, LAYOUT_FILE_NAME, UI_WATCHER_TIME_INTERVAL, ACTIVITY_INFO_FILE_NAME
from lib.Common import deleteFile
from lib.RunStatus import RunStatus
import platform
import json


class DeviceConnect:

    def __init__(self, logger, udid: str = ""):

        self.udid = udid
        self.logger = logger
        if self.udid is not "":
            self.logger.info("init uiautomatior2 in %s" % self.udid)
            self.device = uiautomator2.connect(udid)
        else:
            self.logger.info("init uiautomatior2 in default device")
            self.device = uiautomator2.connect()

        self.appInstallStatus = True  # app安装状态
        self.dumpErrCount = 0
        reratio = self.device.window_size()
        self.screenw = reratio[0]
        self.screenh = reratio[1]

        pass

    def __saveScreenshot(self, filepath):

        self.device.screenshot(filepath)
        pass

    def __saveLayoutXML(self, filepath):

        xml = self.device.dump_hierarchy()
        file = open(filepath, 'w', encoding='utf-8')
        file.write(xml)
        file.close()
        pass

    def __saveActivityInfo(self, filepath):
        # dump activity 和 屏幕分辨率信息
        activityInfo = self.device.app_current()
        activityInfo['width'] = self.screenw
        activityInfo['height'] = self.screenh

        file = open(filepath, 'w', encoding='utf-8')
        file.write(json.dumps(activityInfo))
        file.close()

        pass

    def dumpUI(self, outputdir, dumpcount):

        timestamp = round(time.time() * 1000)
        dirpath = os.path.join(outputdir, "ui_%d_%d" % (dumpcount, timestamp))
        os.makedirs(dirpath)
        screenshotpath = os.path.join(dirpath, SCREENSHOT_FILE_NAME)
        layoutxmlpath = os.path.join(dirpath, LAYOUT_FILE_NAME)
        activitypath = os.path.join(dirpath, ACTIVITY_INFO_FILE_NAME)

        try:
            self.__saveScreenshot(screenshotpath)
        except Exception as e:
            self.logger.error("err in save screenshot, Reason:%s" % e)
            self.dumpErrCount += 1
            if self.dumpErrCount >= 3:
                return RunStatus.UI2_ERROR

        try:
            self.__saveLayoutXML(layoutxmlpath)
        except Exception as e:
            self.logger.error("err in save layout, Reason:%s" % e)
            self.dumpErrCount += 1
            if self.dumpErrCount >= 3:
                return RunStatus.UI2_ERROR
        
        try:
            self.__saveActivityInfo(activitypath)
        except Exception as e:
            self.logger.error("err in save activity info, Reason:%s" % e)
            self.dumpErrCount += 1
            if self.dumpErrCount >= 3:
                return RunStatus.UI2_ERROR

        return RunStatus.SUCCESS

    def startApp(self, pkgname=""):

        try:
            self.logger.info("start app: " + pkgname)
            self.device.app_start(pkgname, use_monkey=True)
        except Exception as e:
            self.logger.error("uiautomator2 start app err, Reason: %s" % e)
            return RunStatus.UI2_ERROR

        time.sleep(1)
        return RunStatus.SUCCESS

    def stopApp(self, pkgname=""):

        self.logger.info("stop app: " + pkgname)
        self.device.app_stop(pkgname)
        self.device.app_clear(pkgname)

        time.sleep(1)
        pass

    def getCurrentPackage(self):

        return self.device.app_current()["package"]

    def pressHome(self):

        self.device.press("home")

    def getCurrentApp(self):

        curapp = ""
        try:
            curapp = self.device.app_current()
        except OSError:
            self.logger.error("Couldn't get focused app")

        return curapp

    def getInstalledApps(self):

        return self.device.app_list()

    def installApk(self, pkgname, remoteApkPath=""):

        self.logger.info("start install " + pkgname)
        if remoteApkPath == "":
            return RunStatus.FILE_NOT_FIND

        if remoteApkPath.startswith("http"):
            self.logger.info('download apk from %s' % remoteApkPath)
            try:
                urllib.request.urlretrieve(remoteApkPath, 'tmp_%s.apk' % pkgname)
            except Exception as e:
                self.logger.error("download %s from %s failed!" % (pkgname, remoteApkPath))
                return RunStatus.DOWNLOAD_ERR
            remoteApkPath = 'tmp_%s.apk' % pkgname

        try:
            output = subprocess.check_output('adb -s %s install -r %s' % (self.udid, remoteApkPath),
                                             shell=True).decode()
        except subprocess.CalledProcessError:
            self.logger.error("app install failed!")
            return RunStatus.APK_INSTALL_ERR
        except Exception:
            self.logger.error("app install cmd exec failed!")
            return RunStatus.CMD_EXEC_ERR

        time.sleep(1)
        if pkgname not in self.getInstalledApps():
            self.logger.error("app install failed! reason: %s" % output)
            return RunStatus.APK_INSTALL_ERR

        self.logger.info("app: %s installed successfully." % pkgname)
        return RunStatus.SUCCESS

    def uninstallApk(self, pkgname):

        self.logger.info("start uninstall " + pkgname)
        status = self.device.app_uninstall(pkgname)
        if status:
            self.logger.info("finish uninstall " + pkgname)
        else:
            self.logger.warning("err in uninstall %s, please check" % pkgname)

        delFilePath = 'tmp_%s.apk' % pkgname
        try:
            self.logger.info("delete file %s" % delFilePath)
            deleteFile(delFilePath)
        except Exception as ee:
            self.logger.warning("delete %s failed! %s" % (delFilePath, ee))
        pass

    def getAppInstallStatus(self):

        return self.appInstallStatus

    def startWatchers(self):

        # 权限申请回调
        self.device.watcher("PERMISSION_ALLOW").when(
            xpath="//android.widget.Button[@resource-id='com.android.packageinstaller:id/permission_allow_button']"
        ).click()

        # Google登录回调
        # Google 登录框可以点击的是com.google.android.gms:id/account_name的父节点的父节点
        self.device.watcher("GOOGLE_LOGIN").when(
            xpath="//android.widget.TextView[@resource-id='com.google.android.gms:id/account_name']/../.."
        ).click()

        # 在登录界面就不要随机触发了，直接点google账号绑定就完事了
        # 直接点带Google字样的会有问题，目前看到都是按钮; 还有一部分是只有图标的，这种layout中描述内容比较少，目前只适配发现的
        # 触发一次就移除该watcher，避免登录不上造成死循环
        def GoogleBindCallbackButton():
            self.device.xpath(
                "//android.widget.Button[re:match(@text, '(?i)(sign|login|bind|continue).*google')]"
            ).click()
            self.device.watcher.remove("GOOGLE_BIND_BUTTON")
            self.device.watcher.remove("GOOGLE_BIND_ICON")
            self.device.watcher.remove("GOOGLE_BIND_TEXT")

        def GoogleBindCallbackText():
            self.device.xpath(
                xpath="//android.widget.TextView[re:match(@text, '(?i)(sign|login|bind|continue).*google')]"
            ).click()
            self.device.watcher.remove("GOOGLE_BIND_BUTTON")
            self.device.watcher.remove("GOOGLE_BIND_ICON")
            self.device.watcher.remove("GOOGLE_BIND_TEXT")

        def GoogleBindCallbackIcon():
            self.device.xpath(
                "//android.widget.ImageView[re:match(@resource-id, '(?i)account.*google')]"
            ).click()
            self.device.watcher.remove("GOOGLE_BIND_BUTTON")
            self.device.watcher.remove("GOOGLE_BIND_ICON")
            self.device.watcher.remove("GOOGLE_BIND_TEXT")

        self.device.watcher("GOOGLE_BIND_BUTTON").when(
            xpath="//android.widget.Button[re:match(@text, '(?i)(sign|login|bind|continue).*google')]"
        ).call(GoogleBindCallbackButton)

        self.device.watcher("GOOGLE_BIND_TEXT").when(
            xpath="//android.widget.TextView[re:match(@text, '(?i)(sign|login|bind|continue).*google')]"
        ).call(GoogleBindCallbackText)

        self.device.watcher("GOOGLE_BIND_ICON").when(
            xpath="//android.widget.ImageView[re:match(@resource-id, '(?i)account.*google')]"
        ).call(GoogleBindCallbackIcon)

        # apk安装失败填出框适配，避免apk问题导致的反复重启
        self.appInstallStatus = True

        def InstallFailCallback():
            self.appInstallStatus = False
            self.device.xpath(
                "//android.widget.Button[re:match(@text, '(?i)close')]"
            ).click()

        self.device.watcher("INSTALL_FAIL").when(
            xpath="//android.widget.TextView[@resource-id='android:id/alertTitle' "
                  "and re:match(@text, '(?i)installation\\s+fail')]"
        ).call(InstallFailCallback)

        # 程序崩溃弹出框 如"Unfortunately, Maps has stopped."
        def StartFailCallback():
            self.device.xpath(
                "//android.widget.Button[re:match(@text, '(?i)ok')]"
            ).click()

        self.device.watcher("START_FAIL").when(
            xpath="//android.widget.TextView[@resource-id='android:id/message' "
                  "and re:match(@text, '(?i)unfortunately.*stopped.')]"
        ).call(StartFailCallback)

        # 7.1.1程序崩溃弹窗
        def StartFailCallback_7():
            self.appInstallStatus = False
            self.device.xpath(
                "//android.widget.Button[re:match(@text, '(?i)Close.*app')]"
            ).click()

        self.device.watcher("START_FAIL_7").when(
            xpath="//android.widget.TextView[@resource-id='android:id/alertTitle' "
                  "and re:match(@text, '(?i).*keeps stopping')]"
        ).call(StartFailCallback_7)

        # 第一次会有重启选项
        def StartFailCallbackFirsrt_7():
            self.device.xpath(
                "//android.widget.Button[re:match(@text, '(?i)Open app again')]"
            ).click()

        self.device.watcher("START_FAIL_First_7").when(
            xpath="//android.widget.TextView[@resource-id='android:id/alertTitle' "
                  "and re:match(@text, '(?i).*has stopped')]"
        ).call(StartFailCallbackFirsrt_7)

        self.device.watcher.start(UI_WATCHER_TIME_INTERVAL)
        self.device.watcher.run()

    def closeWatchers(self):

        self.device.watcher.stop()
        self.device.watcher.reset()
        pass

    def removeWatchers(self, watcherid):

        self.device.watcher.remove(watcherid)
        pass

    def getRunningApps(self):

        runAppList = None
        try:
            runAppList = self.device.app_list_running()
        except Exception:
            self.logger.warning("err in get run app list")

        return runAppList

    def isAppRun(self, pkgname):
    
        runAppList = self.getRunningApps()
        if runAppList is None or pkgname in runAppList:
            return True

        return False
        
    def saveLog(self, outputDir, startTime):

        startTime = time.strftime('%m-%d %H:%M:%S.000', time.localtime(int(startTime) - 5))

        sysType = platform.system()
        if sysType == 'Windows':
            logCmd = ['adb', '-s', self.udid, 'logcat', '-t', startTime, '|',
                    'findstr', 'CODE-BEHAVIOR', '>', os.path.join(outputDir, "apiSeq.txt")]
        else:
            logCmd = ['adb', '-s', self.udid, 'logcat', '-t', startTime, '|',
                    'grep', 'CODE-BEHAVIOR', '>', os.path.join(outputDir, "apiSeq.txt")]
        try:
            subprocess.check_output(logCmd, shell=True)
        except Exception as e:
            self.logger.warning("the api sequence save failed, reason: %s" % e)

        time.sleep(2)

        pass
