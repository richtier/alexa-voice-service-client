from collections import OrderedDict
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from urllib.parse import urlencode, quote, parse_qsl, urlparse


class AmazonAlexaServiceLoginHandler(BaseHTTPRequestHandler):
    oauth2_url = 'https://www.amazon.com/ap/oa'
    oauth2_token_url = 'https://api.amazon.com/auth/o2/token'

    client_id = None
    device_type_id = None
    client_secret = None

    def __init__(
        self, client_id, device_type_id, client_secret, *args, **kwargs
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.device_type_id = device_type_id
        super().__init__(*args, **kwargs)

    @property
    def callback_url(self):
        # note: ensure the redirect url is whitelisted in the
        # 'Allowed Return URLs' section under 'Web Settings' for your
        # Security Profile on Amazon Developer Portal.
        return 'http://{address}:{port}/callback/'.format(
            address=self.server.server_name,
            port=self.server.server_port,
        )

    def do_GET(self):
        routes = {
            '/': self.handle_login,
            '/callback/': self.handle_callback,
        }
        # remove querystring
        path = self.path.split('?')[0]
        if path not in routes:
            self.send_response(404, message='Not Found')
            self.end_headers()
            return
        return routes[path]()

    def handle_login(self):
        self.send_response(302)
         # OrderedDict to facilitate testing
        params = OrderedDict([
            ('client_id', self.client_id),
            ('scope', 'alexa:all'),
            ('scope_data', json.dumps({
                'alexa:all': OrderedDict([
                    ('productID', self.device_type_id),
                    ('productInstanceAttributes', {
                        'deviceSerialNumber': '001'
                    })
                ])
            })),
            ('response_type', 'code'),
            ('redirect_uri', self.callback_url)
        ])

        self.send_header(
            'Location', self.oauth2_url + '?' + urlencode(params)
        )
        self.end_headers()
        return

    def handle_callback(self):
        params = dict(parse_qsl(urlparse(self.path).query))
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': quote(params['code']),
            'grant_type': 'authorization_code',
            'redirect_uri': self.callback_url,
        }
        response = requests.post(self.oauth2_token_url, json=payload)
        if response.status_code != 200:
            self.send_response(response.status_code)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.content)
        else:
            self.send_response(response.status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.content)
        return
