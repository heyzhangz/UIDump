import time


class Timer:

    def __init__(self, duration=1800000):

        self.duration = duration
        self.starttime = time.time() * 1000

        pass

    def start(self):

        self.starttime = time.time() * 1000
        pass

    def isFinish(self):

        nowtime = time.time() * 1000
        if nowtime - self.starttime >= self.duration:
            return True

        return False
