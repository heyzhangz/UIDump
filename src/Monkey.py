import os
import re
import subprocess
import time

from GlobalConfig import MONKEY_WHITE_LIST_PATH, MONKEY_LOG_NAME, MONKEY_TIME_INTERVAL, MONKEY_WHITE_LIST_NAME


class Monkey:

    def __init__(self, logger, outdir, udid="", timeInterval=MONKEY_TIME_INTERVAL, pkgname=""):

        if udid == "":
            raise Exception("no target device in monkey")
        self.udid = udid
        self.logger = logger
        self.logger.info("init monkey in %s" % self.udid)
        self.timeInterval = timeInterval
        self.packagename = pkgname
        self.logdir = outdir
        # 把白名单推到临时目录
        self.__pushWhiteList()

        pass

    def __checkWhiteList(self):

        checkcmd = 'adb -s %s shell "[ -e /data/local/tmp/%s ] && echo 1 || echo 0"' \
                   % (self.udid, MONKEY_WHITE_LIST_PATH)
        output = subprocess.check_output(checkcmd, shell=True).decode().strip()

        if output is "1":
            return True
        else:
            return False

    def __pushWhiteList(self):

        self.logger.info("push white list to /data/local/tmp/")
        pushcmd = 'adb -s %s push %s /data/local/tmp/' \
                  % (self.udid, os.path.join(os.path.abspath('.'), MONKEY_WHITE_LIST_PATH))
        subprocess.Popen(pushcmd, shell=True)

        pass

    def startMonkey(self):

        monkeycmd = 'adb -s %s shell monkey ' % self.udid
        if self.packagename is not "":
            monkeycmd += '-p ' + self.packagename + ' '
        monkeycmd += '--ignore-timeouts --ignore-crashes --kill-process-after-error ' \
                     '--pct-syskeys 0 --pct-rotation 0 --pkg-whitelist-file %s ' \
                     '--throttle %s -v -v -v %s >> %s &' \
                     % ('/data/local/tmp/' + MONKEY_WHITE_LIST_NAME, self.timeInterval, 400000000,
                        os.path.join(self.logdir, MONKEY_LOG_NAME))

        subprocess.Popen(monkeycmd, shell=True)
        pass

    def stopMonkey(self):

        for i in range(10):
            cmd_pid = ["adb", "-s", self.udid, "shell", "ps", "|", "grep", "monkey"]
            output = subprocess.check_output(cmd_pid).decode()

            if output == '':
                self.logger.info("No monkey running")
                break
            else:
                output = re.search('shell {5}[0-9]+', output).group()
                pid = re.search('[0-9]+', output).group()
                self.logger.info("kill the monkey process: %s" % pid)
                subprocess.check_output("adb -s %s shell kill %s" % (self.udid, pid))

        time.sleep(2)
        pass
