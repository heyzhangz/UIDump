import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] - %(filename)s[l:%(lineno)d] : %(message)s')

logger = logging.getLogger()
