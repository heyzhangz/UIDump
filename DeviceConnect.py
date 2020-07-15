import os
import subprocess
import time
import traceback
import urllib.request

import uiautomator2

from Logger import logger

TMP_APK_FILE_PATH = os.path.join(os.path.abspath('.'), 'installtmp.apk')
WHITE_LIST_PATH = os.path.join(os.path.abspath('.'), 'monkey_pkg_whitelist.txt')


class DeviceConnect:
    device = None

    def __init__(self):

        self.device = uiautomator2.connect()
        self.installstatus = True
        # self.stop_sysapp_list = [] # 白名单app 停止dump的时候要一并关掉
        #
        # with open(WHITE_LIST_PATH, 'r') as f:
        #     for line in f.readlines():
        #         line = line.strip()
        #         self.stop_sysapp_list.append(line)

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
        dirpath = os.path.join(outputdir, "ui_" + str(dumpcount) + "_" + str(timestamp))
        os.makedirs(dirpath)
        screenshotpath = os.path.join(dirpath, "screenshot.jpg")
        layoutxmlpath = os.path.join(dirpath, "layout.xml")

        self.__saveScreenshot(screenshotpath)
        self.__saveLayoutXML(layoutxmlpath)
        pass

    def stopApp(self, pkgname=""):

        if pkgname != "":
            logger.info("stop app: " + pkgname)
            self.device.app_stop(pkgname)
            self.device.app_clear(pkgname)

        # 关闭白名单APP
        # running_apps = self.getRunningApps()
        # for sysapp in self.stop_sysapp_list:
        #     if sysapp in running_apps:
        #         logger.info("stop app: " + sysapp)
        #         self.device.app_stop(sysapp)
        #         self.device.app_clear(sysapp)

        time.sleep(2)
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
            return False

        if remoteApkPath.startswith("http"):
            logger.info('Download apk from %s' % remoteApkPath)
            urllib.request.urlretrieve(remoteApkPath, TMP_APK_FILE_PATH)
            remoteApkPath = TMP_APK_FILE_PATH

        subprocess.check_output('adb install -r %s' % remoteApkPath, shell=True).decode()

        if pkgname not in self.getInstalledApps():
            logger.error("App installed failed.")
            return False

        logger.info("App: %s installed successfully." % pkgname)
        return True

    def uninstallApk(self, pkgname):

        logger.info("start uninstall " + pkgname)
        status = self.device.app_uninstall(pkgname)
        if status:
            logger.info("finish uninstall " + pkgname)
        else:
            logger.warning("err in uninstall %s, please check" % pkgname)

        self.deleteInstallFile()
        pass

    def deleteInstallFile(self):

        if os.path.exists(TMP_APK_FILE_PATH):
            logger.info("delete tmp apk file")
            try:
                os.remove(TMP_APK_FILE_PATH)
            except Exception as e:
                logger.warning("delete tmp apk file failed! %s" % e)
                traceback.print_exc()

        pass

    def getAppInstallStatus(self):

        return self.installstatus

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
        self.installstatus = True

        def InstallFailCallback():
            self.installstatus = False
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

        self.device.watcher.start(1)
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


device = DeviceConnect()

if __name__ == "__main__":
    device.stopApp("com.thetrainline")
