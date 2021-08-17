import logging
import os
import sys


def setup_logger(name, distributed_rank, save_dir=None, mode="train"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # don't log results for the non-master process
    if distributed_rank > 0:
        return logger
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    if save_dir:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        fh = logging.FileHandler(os.path.join(save_dir, 'log_{}.txt'.format(mode)))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

def close_logger(name):
    logger = logging.getLogger(name)
    if len(logger.handlers) < 2:
        return
    logger.removeHandler(logger.handlers[0])
    logger.handlers[0].stream.close()
    logger.removeHandler(logger.handlers[0])

def print_log(msg, logger=None, level=logging.INFO):
    """Print a log message.

    Args:
        msg (str): The message to be logged.
        logger (logging.Logger | str | None): The logger to be used. Some
            special loggers are:
            - "root": the root logger obtained with `get_root_logger()`.
            - "silent": no message will be printed.
            - None: The `print()` method will be used to print log messages.
        level (int): Logging level. Only available when `logger` is a Logger
            object or "root".
    """
    if logger is None:
        print(msg)
    elif isinstance(logger, logging.Logger):
        logger.log(level, msg)
    elif logger != 'silent':
        raise TypeError(
            'logger should be either a logging.Logger object, "root", '
            '"silent" or None, but got {}'.format(logger))
