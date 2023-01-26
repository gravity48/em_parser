import json
from http.cookies import SimpleCookie
import ast

import aiohttp
from settings import LOGIN, PASSWORD, API_URL, COOKIES
from .engine import AiohttpWrapper


async def initialize():
    params = {
        'c': 'portal',
    }
    async with AiohttpWrapper(API_URL) as api:
        await api.get()


async def login():
    get_params = {
        'c': 'portal',
    }
    params = {
        'c': 'main',
        'm': 'index',
        'method': 'Logon',
        'login': 'KovyrshinOL',
    }
    data = {
        'login': 'KovyrshinOL',
        'psw': '123456w',
        'swUserRegion': '',
        'swUserDBType': ''
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest',
    }
    cookies = COOKIES
    async with aiohttp.ClientSession(headers=headers) as session:
        '''
        print(session.cookie_jar.filter_cookies(API_URL))
        response = await session.post(API_URL, params=params,
                                      data='login=KovyrshinOL&psw=123456w&swUserRegion=&swUserDBType=')
        result = await response.text()
        print(result)
        '''
        print(session.cookie_jar.filter_cookies(API_URL))
        data = {
            'object': 'LpuSection',
            'object_id': 'LpuSection_id',
            'object_value': 99560025221,
            'level': 0,
            'LpuSection_id': 99560025221,
            'ARMType': 'stac',
            'date': '24.01.2023',
            'filter_Person_F': '',
            'filter_Person_I': '',
            'filter_Person_O': '',
            'filter_PSNumCard': '',
            'filter_Person_BirthDay': '',
            'filter_MedStaffFact_id': '',
            'MedService_id': 0,
            'node': 'root',
        }
        response = await session.post(API_URL, params={
            'c': 'EvnSection',
            'm': 'getSectionTreeData',
        }, data=data)
        result = await response.text()
        print(session.cookie_jar.filter_cookies(API_URL))
        print(result)
        result = json.loads(result)
        print(result)


pass


async def logout():
    params = {
        'c': 'main',
        'm': 'Logout'
    }
    async with AiohttpWrapper(API_URL) as api:
        await api.get()
    pass


__all__ = ['login', 'logout', 'initialize']
