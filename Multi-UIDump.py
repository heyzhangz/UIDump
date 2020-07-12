import json
import os
import re
import traceback

from UIDump import startUIDump


def readAPPList(filepath):
    if not os.path.exists(filepath):
        print("not found file " + filepath)
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        resjson = json.load(f)
        return resjson


if __name__ == "__main__":
    resjson = readAPPList(os.path.join(os.path.abspath("."), "category_top.json"))
    print(resjson)

    for k, arr in resjson.items():
        # if k == 'Photography':
        #     continue
        category = k
        for apkpath in arr[:10]:
            pkgname = re.search(r'(?:/top/)(.*)(?:/)', apkpath).group(1)
            newpath = 'http://10.141.209.136:8002/' + apkpath[6:]
            RECORD_ROOT_PATH = os.path.join(".", "output", "record", category)

            try:
                startUIDump(['-p', pkgname, '-m', "1800000", '--apkfile', newpath, '-o', RECORD_ROOT_PATH])
                # startUIDump(['-p', pkgname, '-m', "18000", '--apkfile', newpath, '-o', RECORD_ROOT_PATH])
            except Exception as e:
                print("[Error] UIDump " + pkgname + " failed")
                print(e)
                print(traceback.format_exc())
