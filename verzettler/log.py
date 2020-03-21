#!/usr/bin/env python3

# std
import logging

# 3rd
import colorlog


def get_logger(name="Logger", level=logging.WARNING, sh_level=logging.DEBUG):
    """Sets up a logging.Logger.

    If the colorlog module is available, the logger will use colors,
    otherwise it will be in b/w. The colorlog module is available at
    https://github.com/borntyping/python-colorlog but can also easily be
    installed with e.g. 'sudo pip3 colorlog' or similar commands.

    Args:
        name: name of the logger
        level: General logging level
        sh_level: Logging level of stream handler

    Returns:
        Logger
    """
    _logger = colorlog.getLogger(name)

    if _logger.handlers:
        # the logger already has handlers attached to it, even though
        # we didn't add it ==> logging.get_logger got us an existing
        # logger ==> we don't need to do anything
        return _logger

    _logger.setLevel(level)
    if colorlog is not None:
        sh = colorlog.StreamHandler()
        log_colors = {
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red",
        }
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(name)s:%(levelname)s:%(message)s",
            log_colors=log_colors,
        )
    else:
        # no colorlog available:
        sh = logging.StreamHandler()
        formatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
    sh.setFormatter(formatter)
    sh.setLevel(sh_level)
    _logger.addHandler(sh)

    return _logger


logger = get_logger("verzettler")


if __name__ == "__main__":
    # Test the color scheme for the logger.
    lg = get_logger("test")
    lg.setLevel(logging.DEBUG)
    lg.debug("Test debug message")
    lg.info("Test info message")
    lg.warning("Test warning message")
    lg.error("Test error message")
    lg.critical("Test critical message")
