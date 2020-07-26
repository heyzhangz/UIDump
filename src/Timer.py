import time


class Timer:

    def __init__(self, logger, duration=0, stopcondition=None, device=None):

        self.logger = logger
        self.duration = duration
        self.startTime = time.time()
        self.stopCondition = stopcondition
        self.device = device

        pass

    def start(self):

        self.startTime = time.time()
        return self.startTime

    def isFinish(self):

        if self.stopCondition is not None:
            if self.device is None:
                self.logger.warning("no device ?")
                return True
            nowapp = self.device.getCurrentApp()
            if nowapp is not "" and nowapp == self.stopCondition:
                self.logger.info("the record is end by manual")
                return True
        else:
            nowtime = time.time()
            startTime = self.startTime
            if (nowtime - startTime) * 1000 >= self.duration:
                self.logger.info("%s record time is end" % self.device.udid)
                return True

        return False
