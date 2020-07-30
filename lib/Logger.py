import logging
import os

from GlobalConfig import LOG_LEVEL


def initLogger(loggerName=None, outputPath=None, udid=None):
    logger = logging.getLogger(loggerName) if loggerName else logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logLevel = LOG_LEVEL
    if udid:
        formatter = logging.Formatter(fmt='(%(asctime)s)-[%(levelname)s] %(filename)s[l:%(lineno)d]'
                                          ': <%(udid)s> %(message)s',
                                      datefmt='%m/%d %H:%M:%S')
    else:
        formatter = logging.Formatter(fmt='(%(asctime)s)-[%(levelname)s] %(filename)s[l:%(lineno)d]: %(message)s',
                                      datefmt='%m/%d %H:%M:%S')
    
    # 清除一下handler，否则重复记录日志
    hdlrs = []
    for hdlr in logger.handlers:
        hdlrs.append(hdlr)
    for hdlr in hdlrs:
        logger.removeHandler(hdlr)

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

    return logging.LoggerAdapter(logger, extra={'udid': udid})
