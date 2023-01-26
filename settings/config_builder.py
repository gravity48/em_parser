from abc import abstractmethod, ABCMeta, ABC
import configparser
from configparser import SectionProxy


class AbstractConfBuilder(ABC):

    @abstractmethod
    def set_cookies(self, value):
        pass


class TxtConfBuilder(AbstractConfBuilder):

    def __init__(self, conf_file: str):
        self._file = conf_file
        self.config = configparser.ConfigParser()
        self.config.read(conf_file)

    def cookies(self):
        return {key.upper(): value for key, value in self.config['COOKIES'].items()}

    def set_cookies(self, value: str):
        self.config['COOKIES']['PHPSESSID'] = value
        self._save()

    def _save(self):
        with open(self._file, 'w') as f:
            self.config.write(f)

    def update_cookies(self, value):
        return

    def get_login(self) -> str:
        return self.config['AUTH']['login']

    def get_password(self) -> str:
        return self.config['AUTH']['password']

    def get_api_url(self) -> str:
        return self.config['API']['url']

    def get_bot_token(self) -> str:
        return self.config['BOT']['api_token']

    def get_task_timeout(self) -> int:
        return self.config['TASKS'].getint('interval')



