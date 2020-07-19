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

        self.record = {}
        if self.appQueue:
            for udid in self.udids:
                worker = Worker.start(name='worker-%s' % udid, udid=udid)
                self.record[worker] = udid
                self.aliveWorkers.append(worker)

            self.logger.info('Begin dispatch...')

            for worker in self.aliveWorkers:
                app = self.appQueue.pop()
                self.logger.info('Dispatch worker-%s : %s' % (self.record[worker], app.pkgname))
                worker.tell({'apkpath': app.apkpath, 'pkgname': app.pkgname, 'currentworker': self.actor_ref})

            self.aliveWorkersNum = len(self.aliveWorkers)
            self.logger.info('Workers num: %s' % self.aliveWorkersNum)
        else:
            self.logger.error('App list is empty! End!')
            self.stop()

    def on_receive(self, message: dict):

        return_worker = message.get('worker')
        error_flag = message.get('iserror')
        if error_flag:
            self.logger.error('%s finish testing %s with error!' % (return_worker.name, return_worker.pkgname))
            # self.appQueue.append(return_worker.app)
        else:
            self.logger.info('%s finish testing %s!' % (return_worker.name, return_worker.pkgname))

        if len(self.appQueue) > 0:
            # Stop using the device
            app = self.appQueue.pop()
            self.logger.info('Dispatch %s : %s' % (return_worker.name, app.pkgname))
            return_worker.actor_ref.tell(
                {'apkpath': app.apkpath, 'pkgname': app.pkgname, 'currentworker': self.actor_ref})
        else:
            self.logger.info('app queue is empty. Stop %s' % return_worker.name)
            return_worker.actor_ref.stop()
            self.aliveWorkers.remove(return_worker)
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

    def __init__(self, name: str, udid: str):
        super(Worker, self).__init__()
        self.name = name
        self.udid = udid
        self.apkPath = ''
        self.pkgname = ''

    def on_receive(self, message: dict):
        self.apkPath = message.get('apkpath')
        self.pkgname = message.get('pkgname')
        currentWork = message.get('currentworker')

        try:
            # ud = UIDump(['-p', self.pkgname, '-m', "1800000", '--apkfile', self.apkPath])
            ud = UIDump(['-p', self.pkgname, '-m', "36000", '--apkfile', self.apkPath, '-d', self.udid])
            ud.startUIDump()
        except Exception as e:
            print(e)
            print("[Error] UIDump " + self.pkgname + " failed")
            is_error = True
            time.sleep(120)
        else:
            is_error = False

        currentWork.tell({'worker': self, 'iserror': is_error})
