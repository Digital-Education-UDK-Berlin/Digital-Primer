import logging

def initalize_logger(logger_name):
    logger = logging.getLogger(logger_name)      #this will need to get the session somehow
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(logger_name + ".log")    #this will need to get the session ID somehow
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(process)s - (%(threadName)-9s) - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info('logger initalized')
    return logger
