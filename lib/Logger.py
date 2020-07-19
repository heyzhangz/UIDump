import logging
import os

from GlobalConfig import LOG_LEVEL


def initLogger(loggerName=None, outputPath=None):
    logger = logging.getLogger(loggerName) if loggerName else logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logLevel = LOG_LEVEL
    formatter = logging.Formatter(fmt='(%(asctime)s)-[%(levelname)s] - %(filename)s[l:%(lineno)d] : %(message)s',
                                  datefmt='%Y%m%d%H%M')

    printHandler = logging.StreamHandler()
    printHandler.setFormatter(formatter)
    printHandler.setLevel(logLevel)
    logger.addHandler(printHandler)

    if outputPath:
        outputdir = os.path.dirname(outputPath)
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        fileHandler = logging.FileHandler(outputPath, mode='a', encoding='utf-8')
        fileHandler.setFormatter(formatter)
        fileHandler.setLevel(logLevel)
        logger.addHandler(fileHandler)

    return logger
