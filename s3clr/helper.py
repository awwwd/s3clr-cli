"""
Contains all the helper functions
"""


def get_logger(name=__file__, logfile_name='s3-cleanup-runtime'):
    from datetime import datetime
    import logging
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    s_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('{}-{:%Y-%m-%d}.log'.format(logfile_name, datetime.now()))
    s_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    logger.addHandler(s_handler), logger.addHandler(f_handler)
    return logger


