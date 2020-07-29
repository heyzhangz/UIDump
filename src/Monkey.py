import os
import re
import subprocess
import time

from GlobalConfig import MONKEY_WHITE_LIST_PATH, MONKEY_LOG_NAME, MONKEY_TIME_INTERVAL, MONKEY_WHITE_LIST_NAME
from lib.RunStatus import RunStatus


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

        try:
            monkeycmd = 'adb -s %s shell monkey ' % self.udid
            if self.packagename is not "":
                monkeycmd += '-p ' + self.packagename + ' '
            monkeycmd += '--ignore-timeouts --ignore-crashes --kill-process-after-error ' \
                         '--pct-syskeys 0 --pct-rotation 0 --pct-appswitch 5 --pkg-whitelist-file %s ' \
                         '--throttle %s -v %s >> %s &' \
                         % ('/data/local/tmp/' + MONKEY_WHITE_LIST_NAME, self.timeInterval, 400000000,
                            os.path.join(self.logdir, MONKEY_LOG_NAME))

            subprocess.Popen(monkeycmd, shell=True)
        except Exception as e:
            self.logger.error("monkey start error!")
            return RunStatus.MONKEY_ERR

        return RunStatus.SUCCESS

    def stopMonkey(self):

        cmd_pid = ["adb", "-s", self.udid, "shell", "ps", "|", "grep", "monkey"]
        try:
            output = subprocess.check_output(cmd_pid, timeout=5).decode()
        except Exception as e:
            self.logger.warning("err in find monkey process, maybe block in winserver! Reason: %s", e)
            return False

        if output == '':
            self.logger.info("No monkey running")
        else:
            # 全是坑 有shell 有root的
            pid = re.search('\\S+ +([0-9]+)', output).group(1)
            self.logger.info("kill the monkey process: %s" % pid)
            subprocess.check_output("adb -s %s shell kill %s" % (self.udid, pid))
            time.sleep(2)
            
            return True
        
        return False
