import logging
import datetime

class Log:
    def __init__(self, path, prefix: str = '') -> None:
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        prefix_strip = prefix
        if prefix:
            prefix_strip = prefix.replace(' ', '')

        full_path = path + '\\log\\' + prefix_strip + '_' + self.datetime() + '.log'
        file_handler = logging.FileHandler(full_path, encoding='utf8')
        stream_handler = logging.StreamHandler()

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

        pass

    def datetime(self):
        dt = self.now()
        datetime = dt.replace(' ', '_')
        datetime = datetime.replace('-', '')
        datetime = datetime.replace(':', '')

        return datetime.split('.')[0]
    
    def now(self):
        return str(datetime.datetime.now())

    def info(self, text):
        self.logger.info(f'{self.now()} {text}')
        pass

    def error(self, text):
        self.logger.error(f'{self.now()} {text}')
        pass

    pass