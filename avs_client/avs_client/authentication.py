import json

import requests

from avs_client.avs_client import helpers


class AlexaVoiceServiceTokenAuthenticator:
    url = 'https://api.amazon.com/auth/o2/token'

    def __init__(self, client_id, secret, refresh_token):
        self.client_id = client_id
        self.secret = secret
        self.refresh_token = refresh_token

    @helpers.expiring_memo(ttl=(60*60)-30)
    def retrieve_api_token(self) -> str:
        """
        Retrieve the access token from AVS.

        This function is memoized, so the
        value returned by the function will be remembered and returned by
        subsequent calls until the memo expires. This is because the access
        token lasts for one hour, then a new token needs to be requested.

        Decorators:
            helpers.expiring_memo

        Returns:
            str -- The access token for communicating with AVS

        """

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

    def get_headers(self) -> dict:
        return {
            'Authorization': 'Bearer {0}'.format(self.retrieve_api_token())
        }
