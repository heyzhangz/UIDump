
import os
import time
from datetime import datetime

import pykka

from GlobalConfig import MONKEY_TIME, BASE_PATH
from UIDump import UIDump
from lib.Common import saveJsonFile


class Dispatch(pykka.ThreadingActor):

    def __init__(self, logger, appQueue: list, udidList: list):

        super(Dispatch, self).__init__()
        self.appQueue = appQueue
        self.aliveWorkers = []
        self.startTime = datetime.now()
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
                self.aliveWorkers.append(worker)
                self.errorAppList[udid] = []
            else:
                self.logger.warning('Apps is less than workers')
                break

        self.logger.info('Workers num: %s' % len(self.aliveWorkers))

        pass

    def on_receive(self, message: dict):

        returnWorker = message.get('worker')
        errorFlag = message.get('iserror')
        if errorFlag:
            self.logger.error('%s finish testing %s with error!' % (returnWorker.name, returnWorker.pkgname))
            # self.appQueue.append(return_worker.app)
            self.errorAppList[returnWorker.udid].append([returnWorker.pkgname, returnWorker.apkPath])
        else:
            self.logger.info('%s finish testing %s!' % (returnWorker.name, returnWorker.pkgname))

        if self.appQueue:
            app = self.appQueue.pop()
            self.logger.info('Dispatch %s : %s' % (returnWorker.name, app.pkgname))
            returnWorker.actor_ref.tell({'downloadpath': app['downloadpath'],
                                         'pkgname': app['pkgname'],
                                         'currentworker': self.actor_ref})
        else:
            self.logger.info('app queue is empty. Stop %s' % returnWorker.name)
            returnWorker.actor_ref.stop()
            self.aliveWorkers.remove(returnWorker.actor_ref)
            if len(self.aliveWorkers) == 0:
                self.logger.info('No living worker, stop dispatcher!')
                endTime = datetime.now()
                totalSeconds = (endTime - self.startTime).seconds
                hour = totalSeconds // 3600
                minute = (totalSeconds % 3600) // 60
                second = totalSeconds % 60
                self.logger.info('Consume time : %sh %sm %ss' % (str(hour), str(minute), str(second)))
                self.stop()

                timestamp = time.strftime('%Y%m%d%H%M', time.localtime())
                saveJsonFile(self.errorAppList, os.path.join(BASE_PATH, "err_app_list_%s.json" % timestamp))
                saveJsonFile(self.appQueue, os.path.join(BASE_PATH, "remain_app_list_%s.json" % timestamp))

        pass


class Worker(pykka.ThreadingActor):

    def __init__(self, name: str, udid: str, logger):
        super(Worker, self).__init__()
        self.name = name
        self.udid = udid
        self.apkPath = ''
        self.pkgname = ''
        self.logger = logger

        pass

    def on_receive(self, message: dict):
        self.apkPath = message.get('downloadpath')
        self.pkgname = message.get('pkgname')
        currentWork = message.get('currentworker')

        try:
            ud = UIDump(['-p', self.pkgname, '-m', str(MONKEY_TIME), '--apkfile', self.apkPath, '-d', self.udid])
            ud.startUIDump()
        except Exception as e:
            self.logger.error("UIDump %s failed, reason : %s" % (self.pkgname, e))
            is_error = True
            time.sleep(120)
        else:
            is_error = False

        currentWork.tell({'worker': self, 'iserror': is_error})

        pass
