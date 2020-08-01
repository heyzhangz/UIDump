import os
import time
from datetime import datetime

import pykka

from GlobalConfig import MONKEY_TIME, BASE_PATH
from UIDump import UIDump
from lib.Common import saveJsonFile
from lib.RunStatus import RunStatus, isSuccess, isNeedContinue, isNeedRestart


class Dispatch(pykka.ThreadingActor):

    def __init__(self, logger, appQueue: list, udidList: list):

        super(Dispatch, self).__init__()
        self.appQueue = appQueue
        self.aliveWorkers = []
        self.startTime = time.time()
        self.udids = udidList
        self.logger = logger
        self.errorAppList = {}

        self.logger.info('Begin dispatch task')
        for udid in self.udids:
            if self.appQueue:
                worker = Worker.start(name='worker-%s' % udid, udid=udid, logger=self.logger)
                app = self.appQueue.pop()
                self.logger.info('Dispatch worker-%s : %s' % (udid, app['pkgname']))
                worker.tell({'downloadpath': app['downloadpath'],
                             'pkgname': app['pkgname'],
                             'currentworker': self.actor_ref})
                self.aliveWorkers.insert(0, worker)
            else:
                self.logger.warning('Apps is less than workers')
                break

        self.logger.info('Workers num: %s' % len(self.aliveWorkers))

        pass

    def on_receive(self, message: dict):

        returnWorker = message.get('worker')
        runStatus = message.get('runStatus')
        if not isSuccess(runStatus):
            self.logger.error('%s finish testing %s with error!, status: %s' %
                              (returnWorker.name, returnWorker.pkgname, runStatus))
            if returnWorker.pkgname not in self.errorAppList:
                self.errorAppList[returnWorker.pkgname] = {'lastErrStatus': runStatus.name, 'restartCount': 0}

            # 需要重新安装的APP
            if isNeedContinue(runStatus):
                if self.errorAppList[returnWorker.pkgname]['restartCount'] < 3:
                    self.errorAppList[returnWorker.pkgname]['restartCount'] += 1
                    self.logger.info("%s need restart install, the count = %d" % (
                        returnWorker.pkgname, self.errorAppList[returnWorker.pkgname]['restartCount']))
                    self.appQueue.append({"pkgname": returnWorker.pkgname, "downloadpath": returnWorker.apkPath})

        else:
            self.logger.info('%s finish testing %s success!' % (returnWorker.name, returnWorker.pkgname))
            if returnWorker.pkgname in self.errorAppList:
                del (self.errorAppList[returnWorker.pkgname])

        if self.appQueue:
            app = self.appQueue.pop()
            self.logger.info('Dispatch %s : %s' % (returnWorker.name, app['pkgname']))
            returnWorker.actor_ref.tell({'downloadpath': app['downloadpath'],
                                         'pkgname': app['pkgname'],
                                         'currentworker': self.actor_ref})
        else:
            self.logger.info('app queue is empty. Stop %s' % returnWorker.name)
            returnWorker.actor_ref.stop()
            self.aliveWorkers.remove(returnWorker.actor_ref)
            if len(self.aliveWorkers) == 0:
                self.logger.info('No living worker, stop dispatcher!')
                endTime = time.time()
                totalSeconds = int(endTime - self.startTime)
                hour = totalSeconds // 3600
                minute = (totalSeconds % 3600) // 60
                second = totalSeconds % 60
                self.logger.info('Consume time : %sh %sm %ss' % (str(hour), str(minute), str(second)))
                self.stop()

                timestamp = time.strftime('%Y%m%d%H%M', time.localtime())
                saveJsonFile(self.errorAppList, os.path.join(BASE_PATH, "err_app_list_%s.json" % timestamp))

        pass


class Worker(pykka.ThreadingActor):

    def __init__(self, name: str, udid: str, logger):
        super(Worker, self).__init__()
        self.name = name
        self.udid = udid
        self.apkPath = ''
        self.pkgname = ''
        self.logger = logger
        self.failcount = 0

        pass

    def on_receive(self, message: dict):
        self.apkPath = message.get('downloadpath')
        self.pkgname = message.get('pkgname')
        currentWork = message.get('currentworker')

        try:
            ud = UIDump(['-p', self.pkgname, '-m', MONKEY_TIME, '--apkfile', self.apkPath, '-d', self.udid])
            runStatus = ud.startUIDump()
        except Exception as e:
            self.logger.error("special UIDump %s failed, reason : %s" % (self.pkgname, e))
            runStatus = RunStatus.ERROR
            time.sleep(120)

        if isSuccess(runStatus) and self.failcount > 0:
            self.failcount -= 1

        if isNeedRestart(runStatus):
            self.failcount += 1

        if self.failcount >= 3:
            self.failcount = 0
            # 失败超过3次 重启avd
            self.logger.warning("woker-%s fail count more than three, restart" % self.udid)
            time.sleep(30)
            os.system('adb -s %s reboot' % self.udid)
            time.sleep(120)

        currentWork.tell({'worker': self, 'runStatus': runStatus})

        pass
