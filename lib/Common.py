import os
import traceback

from lib.Logger import logger


def deleteFile(filepath):
    if os.path.exists(filepath):
        logger.info("delete file %s" % filepath)
        try:
            os.remove(filepath)
        except Exception as e:
            logger.warning("delete %s failed! %s" % filepath)
            traceback.print_exc()

    pass
