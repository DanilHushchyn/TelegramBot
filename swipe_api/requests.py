import json
from abc import ABC

import httpx
from aiohttp import payload

from bot import httpx_client
from settings import HOST, USERS


class BaseAPIClient(ABC):

    def __init__(self, user_id):
        self.user = user_id
        self.url = HOST

    def get_headers(self):
        user = USERS.find_one({'user_tg_id': f"{self.user}"})
        return {
            'accept': 'application/json',
            "Authorization": f"Bearer {user['access']}"
        }

    async def refresh_token(self):
        user = USERS.find_one({'user_tg_id': f"{self.user}"})
        data = {
            "refresh": f"{user['refresh']}"
        }
        resp = await httpx_client.post(f'{self.url}/api/v1/token/refresh/', data=data)
        if resp.status_code == 200:
            data = {
                "access": f"{resp.json()['access']}"
            }
            USERS.update_one(filter={'user_tg_id': f"{self.user}"}, update={"$set": data})
            return True, f'{resp.json()["access"]}'
        return False, None

    async def send_request(self, request):
        response = await httpx_client.send(request)
        if response.status_code == 401:
            refresh_status, token = await self.refresh_token()
            if refresh_status:
                request.headers['authorization'] = f"Bearer {token}"
                response = await httpx_client.send(request=request)
                return response.json()
            else:
                return None

        return response.json()


class UserAPIClient(BaseAPIClient):
    async def login(self, data):
        resp: httpx.Response = await httpx_client.post(f'{self.url}api/v1/auth/login/', data=data)
        if resp.status_code == 200:
            data = {
                'user_api_id': f'{resp.json()["user"]["pk"]}',
                'access': f'{resp.json()["access"]}',
                'refresh': f'{resp.json()["refresh"]}',
                'user_tg_id': f'{self.user}',
                'email': f'{resp.json()["user"]["email"]}',
                'first_name': f'{resp.json()["user"]["first_name"]}',
                'last_name': f'{resp.json()["user"]["last_name"]}',
                'is_authenticated': True,
            }
            USERS.update_one(filter={'user_tg_id': str(self.user)}, update={"$set": data}, upsert=True)
            return True
        return False

    async def register(self, data):
        json_data = {
            "email": data['email'],
            "password1": data['password'],
            "password2": data['password'],
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "is_builder": False
        }
        resp: httpx.Response = await httpx_client.post(f'{self.url}api/v1/auth/registration/',
                                                       data=json_data)
        if resp.status_code == 201:
            data = {
                'user_tg_id': f'{self.user}',
                'email': f'{data["email"]}',
                'first_name': f'{data["first_name"]}',
                'last_name': f'{data["last_name"]}',
                'is_authenticated': False,
            }
            USERS.insert_one(data)
            return True
        return False

    async def logout(self):
        await httpx_client.post(f'{self.url}api/v1/auth/logout/')
        data = {
            'is_authenticated': False,
        }
        USERS.update_one(filter={'user_tg_id': str(self.user)}, update={"$set": data})

    async def get_profile(self):
        request = httpx_client.build_request(method='GET', url=f'{self.url}api/v1/auth/profiles/my_profile/',
                                             headers=self.get_headers())
        response = await self.send_request(request)
        return response

    async def get_my_announcements(self):
        request = httpx_client.build_request(method='GET',
                                             url=f'{self.url}api/v1/client/announcements/my_announcements/',
                                             headers=self.get_headers())
        response = await self.send_request(request)
        return response

    async def get_all_announcements(self):
        request = httpx_client.build_request(method='GET', url=f'{self.url}api/v1/client/announcements/',
                                             headers=self.get_headers())
        response = await self.send_request(request)
        return response

    async def get_gallery_for_announcements(self, id):
        request = httpx_client.build_request(method='GET', url=f'{self.url}api/v1/client/announcements/{id}/',
                                             headers=self.get_headers())
        response = await self.send_request(request)
        return response

    async def create_announcement(self, data, main_photo64, gallery64):
        result = {
            "address": data['address'],
            "main_photo": main_photo64,
            "images": gallery64,
            "map_lat": data['geolocation'][0],
            "map_lon": data['geolocation'][1],
            "description": data['description'],
            "grounds_doc": data['grounds_doc'],
            "appointment": data['appointment'],
            "room_count": data['room_count'],
            "layout": data['layout'],
            "living_condition": data['living_condition'],
            "kitchen_square": int(data['kitchen_square']),
            "balcony_or_loggia": data['balcony_or_loggia'],
            "heating_type": data['heating_type'],
            "payment_type": data['payment_type'],
            "agent_commission": data['agent_commission'],
            "communication_type": data['communication_type'],
            "square": int(data['square']),
            "price": int(data['price']),
        }

        request = httpx_client.build_request(method='POST', url=f'{self.url}api/v1/client/announcements/',
                                             headers=self.get_headers(), json=result)
        response = await self.send_request(request)
        return response
