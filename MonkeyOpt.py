import os
import re
import subprocess
import time


class MonkeyBase:

    def __init__(self, timeinterval=300, pkgname=""):
        self.timeinterval = timeinterval
        self.packagename = pkgname
        if not self.__checkWhiteList():
            self.__pushWhiteList()

        pass

    def __checkWhiteList(self):

        checkcmd = 'adb shell "[ -e /data/local/tmp/monkey_pkg_whitelist.txt ] && echo 1 || echo 0"'
        output = subprocess.check_output(checkcmd, shell=True).decode().strip()
        if output is "1":
            return True
        else:
            return False

    def __pushWhiteList(self):

        print("push white list to /data/local/tmp/")
        pushcmd = 'adb push %s /data/local/tmp/' % os.path.join(os.path.abspath('.'), 'monkey_pkg_whitelist.txt')
        subprocess.Popen(pushcmd, shell=True)

        pass

    def startMonkey(self):

        monkeycmd = 'adb shell monkey '
        if self.packagename is not "":
            monkeycmd += '-p ' + self.packagename + ' '
        monkeycmd += '--ignore-timeouts --ignore-crashes --kill-process-after-error ' \
                     '--pct-syskeys 0 --pkg-whitelist-file %s --throttle %s -v -v -v %s' \
                     % ('/data/local/tmp/monkey_pkg_whitelist.txt', self.timeinterval, 400000000)

        subprocess.Popen(monkeycmd, shell=True)
        pass

    def stopMonkey(self):

        for i in range(10):
            output = None
            cmd_pid = "adb shell ps | grep monkey"
            try:
                output = subprocess.check_output(cmd_pid).decode()
            except Exception:
                print("stop error")
            if output == '':
                print("No monkey running")
                break
            else:
                output = re.search('shell {5}[0-9]+', output).group()
                pid = re.search('[0-9]+', output).group()
                print("kill the monkey process: %s" % pid)
                subprocess.check_output("adb shell kill %s" % pid)

        time.sleep(2)
        pass
