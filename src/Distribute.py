import pykka
import time

from UIDump import UIDump


class App:

    def __init__(self, pkgname, apkpath):
        self.pkgname = pkgname
        self.apkpath = apkpath


class Dispatch(pykka.ThreadingActor):

    def __init__(self, logger, appQueue: list, udidList: list):

        super(Dispatch, self).__init__()
        self.appQueue = appQueue
        self.aliveWorkers = []
        self.startTime = time.time()
        self.udids = udidList
        self.logger = logger

        self.logger.info('Begin dispatch task')
        for udid in self.udids:
            worker = Worker.start(name='worker-%s' % udid, udid=udid, logger=self.logger)
            if self.appQueue:
                app = self.appQueue.pop()
                self.logger.info('Dispatch worker-%s : %s' % (udid, app.pkgname))
                worker.tell({'apkpath': app.apkpath, 'pkgname': app.pkgname, 'currentworker': self.actor_ref})
                self.aliveWorkers.append(worker)
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
            # TODO record
        else:
            self.logger.info('%s finish testing %s!' % (returnWorker.name, returnWorker.pkgname))

        if self.appQueue:
            app = self.appQueue.pop()
            self.logger.info('Dispatch %s : %s' % (returnWorker.name, app.pkgname))
            returnWorker.actor_ref.tell(
                {'apkpath': app.apkpath, 'pkgname': app.pkgname, 'currentworker': self.actor_ref})
        else:
            self.logger.info('app queue is empty. Stop %s' % returnWorker.name)
            returnWorker.actor_ref.stop()
            self.aliveWorkers.remove(returnWorker)
            if len(self.aliveWorkers) == 0:
                self.logger.info('No living worker, stop dispatcher!')
                end_time = time.time()
                total = end_time - self.startTime
                hour = total / 3600
                minute = (total % 3600) / 60
                second = total % 60
                self.logger.info('Consume time : ' + str(hour) + 'h' + str(minute) + 'm' + str(second) + 's')
                self.stop()


class Worker(pykka.ThreadingActor):

    def __init__(self, name: str, udid: str, logger):
        super(Worker, self).__init__()
        self.name = name
        self.udid = udid
        self.apkPath = ''
        self.pkgname = ''
        self.logger = logger

    def on_receive(self, message: dict):
        self.apkPath = message.get('apkpath')
        self.pkgname = message.get('pkgname')
        currentWork = message.get('currentworker')

        try:
            # ud = UIDump(['-p', self.pkgname, '-m', "1800000", '--apkfile', self.apkPath])
            ud = UIDump(['-p', self.pkgname, '-m', "36000", '--apkfile', self.apkPath, '-d', self.udid])
            ud.startUIDump()
        except Exception as e:
            self.logger.error("UIDump " + self.pkgname + " failed, reason : " + e)
            is_error = True
            time.sleep(120)
        else:
            is_error = False

        currentWork.tell({'worker': self, 'iserror': is_error})
