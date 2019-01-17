from collections import OrderedDict
import json
from urllib.parse import urlencode, quote


class AmazonOauth2RequestManager:
    authorization_request_url = 'https://www.amazon.com/ap/oa'
    authorization_grant_url = 'https://api.amazon.com/auth/o2/token'
    access_token_url = authorization_grant_url

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_authorization_request_url(self, device_type_id, callback_url):
        # OrderedDict to facilitate testing
        params = OrderedDict([
            ('client_id', self.client_id),
            ('scope', 'alexa:all'),
            ('scope_data', json.dumps({
                'alexa:all': OrderedDict([
                    ('productID', device_type_id),
                    ('productInstanceAttributes', {
                        'deviceSerialNumber': '001'
                    })
                ])
            })),
            ('response_type', 'code'),
            ('redirect_uri', callback_url)
        ])
        return self.authorization_request_url + '?' + urlencode(params)

    def get_authorizarization_grant_params(self, code, callback_url):
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': quote(code),
            'grant_type': 'authorization_code',
            'redirect_uri': callback_url,
        }

    def get_access_token_params(self, refresh_token):
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
