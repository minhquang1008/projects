import logging
import traceback
from logger.to_database import LoggingDBHandler


class Logger:

    def __init__(self, tableName: str) -> None:

        logger = logging.getLogger(__name__)
        handler = LoggingDBHandler(tableName)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        self.logger = logger

    def log(self, func):  # Decorator
        def wrapper(*args,**kwargs):
            try:
                func(*args,**kwargs)
                json = LoggingDBHandler.generateJSON(func.__qualname__,args,kwargs,'OK')
                self.logger.info(json)
            except (Exception,):
                message = traceback.format_exc()
                json = LoggingDBHandler.generateJSON(func.__qualname__,args,kwargs,message)
                self.logger.critical(json)
                raise RuntimeError("Error while running") # raise lỗi để exit
        return wrapper

