import os
import time

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

        return self.device.app_current()

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
    def installApk(self, remote_apk_path = ""):
        if remote_apk_path == "":
            print('no apk file input!')
            return
        self.device.app_install(remote_apk_path)

    def uninstallApk(self, package_name):
        self.device.app_uninstall(package_name)

device = DeviceConnect()
