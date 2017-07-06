import json

import requests

from avs_client import helpers


class AlexaVoiceServiceTokenAuthenticator:
    url = 'https://api.amazon.com/auth/o2/token'

    def __init__(self, client_id, secret, refresh_token):
        self.client_id = client_id
        self.secret = secret
        self.refresh_token = refresh_token

    @helpers.expiring_memo(ttl=3570)
    def retrieve_api_token(self):
        payload = {
            'client_id': self.client_id,
            'client_secret': self.secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token',
        }
        response = requests.post(self.url, json=payload)
        response.raise_for_status()
        response_json = json.loads(response.text)
        return response_json['access_token']

    def prefetch_api_token(self):
        self.retrieve_api_token()

    def get_authentication_headers(self):
        return {
            'Authorization': 'Bearer {0}'.format(self.retrieve_api_token())
        }
