import os
import subprocess
import time


def startRecord(outputdir):
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    filepath = outputdir + "recordevents.txt"
    cmd = "adb shell getevent -tt > " + filepath + " &"
    subprocess.Popen(cmd, shell=True)

    pass


def endRecord(outputdir):

    # 杀进程
    pid = subprocess.getoutput("adb shell pgrep -f getevent")
    subprocess.Popen("adb shell kill " + pid)

    # 转换脚本
    eventpath = outputdir + "recordevents.txt"
    translatepath = outputdir + "replyscript.txt"
    cmd = "java -jar ./lib/ReranTranslator.jar " + eventpath + " " + translatepath
    subprocess.Popen(cmd)

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
    subprocess.Popen(cmd)

    cmd = "adb shell " + androiddir + "replay " + androiddir + filename
    subprocess.Popen(cmd)

    pass


if __name__ == "__main__":
    startRecord("./")
    time.sleep(5)
    endRecord("./")
