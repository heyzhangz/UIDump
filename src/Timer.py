import time


class Timer:

    def __init__(self, logger, duration=0, stopcondition=None, device=None):

        self.logger = logger
        self.duration = duration
        self.startTime = time.time() * 1000
        self.stopCondition = stopcondition
        self.device = device

        pass

    def start(self):

        self.startTime = time.time() * 1000
        pass

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
            nowtime = time.time() * 1000
            if nowtime - self.startTime >= self.duration:
                self.logger.info("the timer is end")
                return True

        return False
