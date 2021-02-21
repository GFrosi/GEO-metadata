import logging
import os.path


def initialize_logger(outputdir, logger):

    # create error file handler and set level to error
    handler = logging.FileHandler(os.path.join(outputdir, "workflow_error.log"),"a", encoding=None, delay="true")
    handler.setLevel(logging.ERROR)
    logging.Formatter()
    formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(message)s", datefmt='%m/%d/%Y %I:%M:%S %p')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join(outputdir, "workflow_debug.log"),"a")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(message)s", datefmt='%m/%d/%Y %I:%M:%S %p')
    handler.setFormatter(formatter)
    logger.addHandler(handler)