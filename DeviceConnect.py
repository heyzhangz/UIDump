import os
import re
import subprocess
import time
import urllib.request


import uiautomator2


class DeviceConnect:
    device = None

    def __init__(self):
        self.device = uiautomator2.connect()
        pass

    def __saveScreenshot(self, filepath):
        # savedir = os.path.dirname(filepath)
        # if not os.path.exists(savedir):
        #     os.makedirs(savedir)

        self.device.screenshot(filepath)

        pass

    def __saveLayoutXML(self, filepath):
        # savedir = os.path.dirname(filepath)
        # if not os.path.exists(savedir):
        #     os.makedirs(savedir)

        xml = self.device.dump_hierarchy()
        file = open(filepath, 'w', encoding='utf-8')
        file.write(xml)
        file.close()

        pass

    def dumpUI(self, outputdir, dumpcount):
        timestamp = round(time.time() * 1000)
        # timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime())
        # dirpath = outputdir + "ui_" + timestamp + "_" + str(dumpcount) + os.sep
        dirpath = os.path.join(outputdir, "ui_" + str(dumpcount) + "_" + str(timestamp))
        os.makedirs(dirpath)
        screenshotpath = os.path.join(dirpath, "screenshot.jpg")
        layoutxmlpath = os.path.join(dirpath, "layout.xml")

        self.__saveScreenshot(screenshotpath)
        self.__saveLayoutXML(layoutxmlpath)

        pass

    def stopApp(self, pacname):

        return self.device.app_stop(pacname)

    def getDeviceModel(self):

        return self.device.device_info["model"]

    def getInfo(self):

        return self.device.info

    def getCurrentPackage(self):

        return self.device.app_current()["package"]

    def getCurrentApp(self):
        curapp = ""
        try:
            curapp = self.device.app_current()
        except OSError:
            print("Couldn't get focused app")

        return curapp

    def pressHome(self):

        self.device.press("home")

    def startApp(self, pacname=""):

        if pacname == "":
            print("no packagename")
            return
        try:
            self.device.app_start(pacname)
        except:
            print("launch 1 fail")

        time.sleep(2)

        if self.getCurrentPackage() != pacname:
            print("am start fail, try to use monkey")
            self.device.app_start(pacname, use_monkey=True)

        return

    def getInstalledApps(self):

        return self.device.app_list()

    def installApk(self, pkgname, remote_apk_path=""):

        if remote_apk_path == "":
            print('no apk file input!')
            return False

        if remote_apk_path.startswith("http"):
            print('download apk from ' + remote_apk_path)
            urllib.request.urlretrieve(remote_apk_path, os.path.join(os.path.abspath('.'), 'instaltmp.apk'))
            remote_apk_path = os.path.join(os.path.abspath('.'), 'instaltmp.apk')

        if pkgname in self.getInstalledApps():
            print('App already exist, now uninstalling and install again...')

        output = subprocess.check_output('adb install %s' % remote_apk_path, shell=True).decode()

        if pkgname in self.getInstalledApps():
            print('App installed successfully.')
            return True

        print('[Error] App installed failed.\nFail Message:\n%s' % '\n'.join(output))
        return False

    def uninstallApk(self, package_name):

        print("start uninstall " + package_name)
        self.device.app_uninstall(package_name)
        print("finish uninstall")

        if os.path.exists(os.path.join(os.path.abspath('.'), 'instaltmp.apk')):
            print("delete tmp apk file")
            try:
                os.remove(os.path.join(os.path.abspath('.'), 'instaltmp.apk'))
            except Exception as e:
                print("delete tmp apk file failed!")
                print(e)

        pass

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

        self.device.watcher.start(1)
        self.device.watcher.run()

    def closeWatchers(self):

        self.device.watcher.stop()
        self.device.watcher.reset()
        pass


device = DeviceConnect()

if __name__ == "__main__":
    print(device.getInstalledApps())
    # device.installApk('com.choiceoflove.dating', 'http://10.141.209.136:8001/skq/BehaviorNas/androzoo/app/top/com.choiceoflove.dating/9392f0c57b5a962775814caf1f6b7930.apk')
    device.uninstallApk('com.choiceoflove.dating')
