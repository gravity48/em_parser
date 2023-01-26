from datetime import datetime
from typing import Callable
import aiohttp
from .abc import ResponseWrapper, AuthData, AuthStatusResponse
from .decorators import auth_decorator


class AiohttpWrapper(ResponseWrapper):

    def __init__(self, url: str, cookies: dict, auth_data: AuthData, auth_status_response: AuthStatusResponse,
                 save_cookies: Callable):
        super(AiohttpWrapper, self).__init__(auth_status_response)
        self.url = url
        self.cookies = cookies
        self.auth_data = auth_data
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self._save_cookies = save_cookies
        self.auth_status_response = auth_status_response

    async def __aenter__(self):
        conn = aiohttp.TCPConnector(limit=10)
        self.session = aiohttp.ClientSession(headers=self.headers, cookies=self.cookies, connector=conn)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    @auth_decorator
    async def get_patient_information(self) -> str:
        params = {
            'c': 'EvnSection',
            'm': 'getSectionTreeData',
        }
        data = {
            'object': 'LpuSection',
            'object_id': 'LpuSection_id',
            'object_value': 99560025221,
            'level': 0,
            'LpuSection_id': 99560025221,
            'ARMType': 'stac',
            'date': datetime.now().strftime('%d.%m.%Y'),
            'filter_Person_F': '',
            'filter_Person_I': '',
            'filter_Person_O': '',
            'filter_PSNumCard': '',
            'filter_Person_BirthDay': '',
            'filter_MedStaffFact_id': '',
            'MedService_id': 0,
            'node': 'root',
        }
        async with self.session.post(self.url, params=params, data=data) as response:
            result = await response.text()
        return result

    @auth_decorator
    async def person_detail_view(self, person_id: int):
        params = {
            'c': 'Evn',
            'm': 'getEvnJournal',
        }
        data = {
            'Person_id': person_id,
            'PersonNotice_IsSend': 2,
            'start': 0,
            'limit': 10,
        }
        async with self.session.post(self.url, params=params, data=data) as response:
            result = await response.text()
        return result

    async def update_cookies(self) -> bool:
        if await self._login():
            self.cookies = self.session.cookie_jar.filter_cookies(self.url)
            self._save_cookies(self.cookies['PHPSESSID'].value)
            return True
        return False

    async def _login(self) -> bool:
        params = {
            'c': 'main',
            'm': 'index',
            'method': 'Logon',
            'login': self.auth_data.username,
        }
        data = {
            'login': self.auth_data.username,
            'psw': self.auth_data.password,
            'swUserRegion': '',
            'swUserDBType': ''
        }
        async with self.session.post(self.url, params=params, data=data) as response:
            result_text: str = await response.text()
        if result_text == self.auth_status_response.success:
            return True
        return False


class ApiWrapper:
    instance: AiohttpWrapper = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            raise NotImplementedError
        return cls.instance

    @classmethod
    def aiohttp_instance(cls, url: str, cookies: dict, auth_data: AuthData, auth_status_response: AuthStatusResponse,
                         save_cookies: Callable):
        cls.instance = AiohttpWrapper(url, cookies, auth_data, auth_status_response, save_cookies)
