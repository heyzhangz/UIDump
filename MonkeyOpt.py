import os
import re
import subprocess
import time

from Logger import logger

MONKEY_PKG_WHITELIST_FILE = 'monkey_pkg_whitelist.txt'


class MonkeyOpt:

    def __init__(self, udid="", timeinterval=300, pkgname=""):

        if udid == "":
            raise Exception("no target device in monkey")
        self.udid = udid
        logger.info("init monkey in %s" % self.udid)
        self.timeinterval = timeinterval
        self.packagename = pkgname
        # if not self.__checkWhiteList():
        #     self.__pushWhiteList()
        self.__pushWhiteList()

        pass

    def __checkWhiteList(self):

        checkcmd = 'adb -s %s shell "[ -e /data/local/tmp/%s ] && echo 1 || echo 0"' \
                   % (self.udid, MONKEY_PKG_WHITELIST_FILE)
        output = subprocess.check_output(checkcmd, shell=True).decode().strip()
        if output is "1":
            return True
        else:
            return False

    def __pushWhiteList(self):

        logger.info("push white list to /data/local/tmp/")
        pushcmd = 'adb -s %s push %s /data/local/tmp/' \
                  % (self.udid, os.path.join(os.path.abspath('.'), MONKEY_PKG_WHITELIST_FILE))
        subprocess.Popen(pushcmd, shell=True)

        pass

    def startMonkey(self):

        monkeycmd = 'adb -s %s shell monkey ' % self.udid
        if self.packagename is not "":
            monkeycmd += '-p ' + self.packagename + ' '
        monkeycmd += '--ignore-timeouts --ignore-crashes --kill-process-after-error ' \
                     '--pct-syskeys 0 --pct-rotation 0 --pkg-whitelist-file %s ' \
                     '--throttle %s -v -v -v %s' \
                     % ('/data/local/tmp/' + MONKEY_PKG_WHITELIST_FILE, self.timeinterval, 400000000)

        subprocess.Popen(monkeycmd, shell=True)
        pass

    def stopMonkey(self):

        for i in range(10):
            output = None
            cmd_pid = ["adb", "-s", self.udid, "shell", "ps", "|", "grep", "monkey"]
            try:
                output = subprocess.check_output(cmd_pid).decode()
            except Exception:
                logger.info("monkey stop error")

            if output == '':
                logger.info("No monkey running")
                break
            else:
                output = re.search('shell {5}[0-9]+', output).group()
                pid = re.search('[0-9]+', output).group()
                logger.info("kill the monkey process: %s" % pid)
                subprocess.check_output("adb -s %s shell kill %s" % (self.udid, pid))

        time.sleep(2)
        pass
