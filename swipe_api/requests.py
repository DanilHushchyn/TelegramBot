from abc import ABC

import httpx


class BaseApiClient(ABC):

    def __init__(self, user_id):
        self.url = URL

    @staticmethod
    def get_client():
        return httpx.AsyncClient(http2=True, follow_redirects=True)
