import json
import os
import re
import sys
import time

rootdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(rootdir)

from GlobalConfig import LOG_OUTPUT_PATH, DEVICE_LIST, APP_LIST_PATH
from lib.Logger import initLogger
from src.Distribute import Dispatch


def readAPPList(filepath):
    if not os.path.exists(filepath):
        print("not found file " + filepath)
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        resjson = json.load(f)
        return resjson


# TODO 列表格式匹配
class UIDumpTask:

    def __init__(self, udids: list = None):
        self.apkList = []
        self.logger = initLogger(loggerName="DispatchLogger",
                                 outputPath=os.path.join(LOG_OUTPUT_PATH, "Dispatch_UIDump_%s.log" %
                                                         time.strftime('%Y%m%d%H%M', time.localtime())))
        # json格式 按类别划分
        # resjson = readAPPList(APP_LIST_PATH)
        # for _, arr in resjson.items():
        #     for apkpath in arr:
        #         pkgname = re.search(r'(?:/top/)(.*)(?:/)', apkpath).group(1)
        #         newpath = 'http://10.141.209.139:8002/' + apkpath[6:]
        #         self.apkList.append({"pkgname": pkgname, "apkpath": apkpath, "downloadpath": newpath})

        for root, _, files in os.walk(r"D:\Download\300apk"):
            for apkfile in files:
                pkgname = apkfile.split("-20")[0]
                newpath = os.path.join(root, apkfile)
                self.apkList.append({"pkgname": pkgname, "apkpath": newpath, "downloadpath": newpath})

        if udids is None or len(udids) == 0:
            self.udids = [line.split('\t')[0] for line in
                          os.popen("adb devices", 'r', 1).read().split('\n') if
                          len(line) != 0 and line.find('\tdevice') != -1]
        else:
            self.udids = udids

    def dispatch(self):
        dispatch = Dispatch.start(logger=self.logger, appQueue=self.apkList, udidList=self.udids)
        while not dispatch.is_alive:
            pass


if __name__ == "__main__":
    udt = UIDumpTask(DEVICE_LIST)
    udt.dispatch()
