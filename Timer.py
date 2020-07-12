import time
from Logger import logger


class Timer:

    def __init__(self, duration=0, stopcondition=None):

        self.duration = duration
        self.starttime = time.time() * 1000
        self.stopcondition = stopcondition

        pass

    def start(self):

        self.starttime = time.time() * 1000
        pass

    def isFinish(self):

        if self.stopcondition is not None:
            from DeviceConnect import device
            nowapp = device.getCurrentApp()
            if nowapp is not "" and nowapp == self.stopcondition:
                return True
        else:
            nowtime = time.time() * 1000
            if nowtime - self.starttime >= self.duration:
                logger.info("the timer is end")
                return True

        return False
