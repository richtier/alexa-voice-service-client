import json

import requests

from alexa_client.alexa_client import helpers
from alexa_client.refreshtoken.helpers import AmazonOauth2RequestManager


class AlexaVoiceServiceTokenAuthenticator:
    url = 'https://api.amazon.com/auth/o2/token'

    def __init__(self, client_id, secret, refresh_token):
        self.refresh_token = refresh_token
        self.oauth2_manager = AmazonOauth2RequestManager(
            client_id=client_id,
            client_secret=secret,
        )

    @helpers.expiring_memo(ttl=(60*60)-30)
    def retrieve_api_token(self):
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

        payload = self.oauth2_manager.get_access_token_params(
            refresh_token=self.refresh_token
        )
        response = requests.post(
            self.oauth2_manager.access_token_url, json=payload
        )
        response.raise_for_status()
        response_json = json.loads(response.text)
        return response_json['access_token']

    def prefetch_api_token(self):
        self.retrieve_api_token()

    def get_headers(self):
        return {
            'Authorization': 'Bearer {0}'.format(self.retrieve_api_token())
        }
