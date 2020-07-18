import os
import subprocess
import time
import traceback
import urllib.request

import uiautomator2

from GlobalConfig import SCREENSHOT_FILE_NAME, LAYOUT_FILE_NAME, UI_WATCHER_TIME_INTERVAL
from lib.Common import deleteFile
from lib.Logger import logger


class DeviceConnect:

    def __init__(self, udid: str = ""):

        self.udid = udid
        if self.udid is not "":
            logger.info("init uiautomatior2 in %s" % self.udid)
            self.device = uiautomator2.connect(udid)
        else:
            logger.info("init uiautomatior2 in default device")
            self.device = uiautomator2.connect()

        self.appInstallStatus = True  # app安装状态

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

    def dumpUI(self, outputdir, dumpcount):

        timestamp = round(time.time() * 1000)
        dirpath = os.path.join(outputdir, "ui_%d_%d" % (dumpcount, timestamp))
        os.makedirs(dirpath)
        screenshotpath = os.path.join(dirpath, SCREENSHOT_FILE_NAME)
        layoutxmlpath = os.path.join(dirpath, LAYOUT_FILE_NAME)

        self.__saveScreenshot(screenshotpath)
        self.__saveLayoutXML(layoutxmlpath)
        pass

    def startApp(self, pkgname=""):

        logger.info("start app: " + pkgname)
        self.device.app_start(pkgname, use_monkey=True)

        time.sleep(1)
        pass

    def stopApp(self, pkgname=""):

        logger.info("stop app: " + pkgname)
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
            logger.error("Couldn't get focused app")

        return curapp

    def getInstalledApps(self):

        return self.device.app_list()

    def installApk(self, pkgname, remoteApkPath=""):

        logger.info("start install " + pkgname)
        if remoteApkPath == "":
            raise Exception("apkpath is null!")

        if remoteApkPath.startswith("http"):
            logger.info('download apk from %s' % remoteApkPath)
            urllib.request.urlretrieve(remoteApkPath, 'tmp_%s.apk' % pkgname)
            remoteApkPath = 'tmp_%s.apk' % pkgname

        output = subprocess.check_output('adb -s %s install -r %s' % (self.udid, remoteApkPath), shell=True).decode()

        time.sleep(1)
        if pkgname not in self.getInstalledApps():
            raise Exception("app install failed! reason: %s" % output)

        logger.info("app: %s installed successfully." % pkgname)
        pass

    def uninstallApk(self, pkgname):

        logger.info("start uninstall " + pkgname)
        status = self.device.app_uninstall(pkgname)
        if status:
            logger.info("finish uninstall " + pkgname)
        else:
            logger.warning("err in uninstall %s, please check" % pkgname)

        deleteFile('tmp_%s.apk' % pkgname)
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

        def GoogleBindCallbackIcon():
            self.device.xpath(
                "//android.widget.ImageView[re:match(@resource-id, '(?i)account.*google')]"
            ).click()
            self.device.watcher.remove("GOOGLE_BIND_BUTTON")
            self.device.watcher.remove("GOOGLE_BIND_ICON")

        self.device.watcher("GOOGLE_BIND_BUTTON").when(
            xpath="//android.widget.Button[re:match(@text, '(?i)(sign|login|bind|continue).*google')]"
        ).call(GoogleBindCallbackButton)

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

        return self.device.app_list_running()

    def isAppRun(self, pkgname):

        if pkgname in self.getRunningApps():
            return True

        return False
