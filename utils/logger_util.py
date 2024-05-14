import logging
import os
def get_logger(logger_name, file_path=None, level=logging.DEBUG, as_default_logger=True) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.propagate = False
    logger.setLevel(level)
    if not file_path:
        file_path = '../logs'
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        
    fh = logging.FileHandler(f'{file_path}/{logger_name}.log')
    fh.setLevel(level)
    logger.addHandler(fh)
    if as_default_logger:
        logging.root = logger
    return logger
