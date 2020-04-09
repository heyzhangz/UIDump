import os
import re
import subprocess
import time

GETEVENT_SP_LIST = {"Nexus 5"}  # 有些设备跑""adb exec-out getevent -tt" log会不全，区分一下


def startRecord(outputdir, devmodel):
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    filepath = outputdir + "recordevents.txt"
    if devmodel in GETEVENT_SP_LIST:
        # 部分设备用adb exec-out跑出结果不全
        cmd = "adb shell getevent -tt > " + filepath + " &"
    else:
        # 使用adb exec-out启动避免event事件太多充满stdout buffer
        cmd = "adb exec-out getevent -tt > " + filepath + " &"
    subprocess.Popen(cmd, shell=True)

    pid = subprocess.check_output("adb shell pgrep -f getevent", shell=True, text=True)
    return re.split("[\\s\r\n]", pid.strip())[-1]


def endRecord(outputdir, pid):
    # 杀进程
    print("adb kill the ps " + pid)
    subprocess.Popen("adb shell kill " + pid, shell=True)

    # 转换脚本
    eventpath = outputdir + "recordevents.txt"
    translatepath = outputdir + "replayscript.txt"
    cmd = "java -jar ./lib/ReranTranslator.jar " + eventpath + " " + translatepath
    subprocess.Popen(cmd, shell=True)

    pass


def startReplay(filepath):
    androiddir = "/data/local/tmp/"
    filename = os.path.basename(filepath)

    # 判断是否有replay文件
    cmd = "adb shell ls " + androiddir + "replay"
    echostr = subprocess.getoutput(cmd)
    if "No" in echostr:
        print("There are not replay in /data/local/tmp/")
        return False

    cmd = "adb push " + filepath + " " + androiddir
    subprocess.Popen(cmd, shell=True)

    cmd = "adb shell " + androiddir + "replay " + androiddir + filename
    subprocess.Popen(cmd, shell=True)

    pass


if __name__ == "__main__":
    startRecord("./")
    time.sleep(5)
    endRecord("./")
