from typing import NamedTuple


class AuthData(NamedTuple):
    username: str
    password: str


class AuthStatusResponse(NamedTuple):
    success: str
    error: str


class ResponseWrapper:
    def __init__(self, auth_status_response: AuthStatusResponse):
        self.auth_status_response = auth_status_response

    async def update_cookies(self) -> bool:
        raise NotImplementedError
