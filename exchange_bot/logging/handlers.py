import re
from logging import handlers


class TimedRotatingFileHandler(handlers.TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.suffix = '%Y-%m'
        self.extMatch = re.compile(r'^\d{2}-\d{2}-\d{4}$')
