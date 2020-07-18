import json
import os
import re
import sys

rootdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(rootdir)

from src.Distribute import Dispatch, App

def readAPPList(filepath):
    if not os.path.exists(filepath):
        print("not found file " + filepath)
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        resjson = json.load(f)
        return resjson


class UIDumpTask:

    def __init__(self, udids=None):
        self.apkList = []
        # json格式 按类别划分
        resjson = readAPPList(os.path.join(os.path.abspath("."), "category_top.json"))
        for _, arr in resjson.items():
            for apkpath in arr:
                pkgname = re.search(r'(?:/top/)(.*)(?:/)', apkpath).group(1)
                newpath = 'http://10.141.209.136:8002/' + apkpath[6:]
                self.apkList.append(App(pkgname=pkgname, apkpath=newpath))

        if udids is None:
            self.udids = [line.split('\t')[0] for line in
                          os.popen("adb devices", 'r', 1).read().split('\n') if
                          len(line) != 0 and line.find('\tdevice') != -1]
        else:
            self.udids = udids

    def dispatch(self):
        dispatch = Dispatch.start(appQueue=self.apkList, udidList=self.udids)
        while not dispatch.is_alive:
            pass


if __name__ == "__main__":
    
    udids = [
        'emulator-5564',
        'emulator-5566'
    ]
    udt = UIDumpTask()
    udt.dispatch()
