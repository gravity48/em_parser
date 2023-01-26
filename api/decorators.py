from functools import wraps
from .abc import ResponseWrapper
from .exceptions import AuthErrorException


def auth_decorator(func):
    @wraps(func)
    async def _wrapper(self: ResponseWrapper, *args, **kwargs):
        result: str = await func(self, *args, **kwargs)
        if result == self.auth_status_response.error:
            if await self.update_cookies():
                result = await func(self, *args, **kwargs)
            else:
                raise AuthErrorException
        return result
    return _wrapper
