import os
import time

import uiautomator2


class DeviceConnect:
    device = None

    def __init__(self):
        self.device = uiautomator2.connect()
        pass

    def __saveScreenshot(self, filepath):
        savedir = os.path.dirname(filepath)
        if not os.path.exists(savedir):
            os.makedirs(savedir)

        self.device.screenshot(filepath)

        pass

    def __saveLayoutXML(self, filepath):
        savedir = os.path.dirname(filepath)
        if not os.path.exists(savedir):
            os.makedirs(savedir)

        xml = self.device.dump_hierarchy()
        file = open(filepath, 'w', encoding='utf-8')
        file.write(xml)
        file.close()

        pass

    def dumpUI(self, outputdir, dumpcount):
        timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime())
        dirpath = outputdir + "ui_" + timestamp + "_" + str(dumpcount) + os.sep
        screenshotpath = dirpath + "screenshot.jpg"
        layoutxmlpath = dirpath + "layout.xml"

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


device = DeviceConnect()
