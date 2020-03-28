import logging
import sys


def custom_logger(logger_name, level=logging.DEBUG):
  """
  returns a custom logger with given name and level
  """
  logger = logging.getLogger(logger_name)
  logger.setLevel(level)
  format_string = "%(levelname)s %(asctime)s - %(message)s"

  log_format = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")

  # creating and adding console handler
  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setFormatter(log_format)
  logger.addHandler(console_handler)

  # creating and adding file handler
  file_handler = logging.FileHandler(logger_name, mode="w")
  file_handler.setFormatter(log_format)
  logger.addHandler(file_handler)

  return logger
