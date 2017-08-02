from collections import OrderedDict
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from urllib.parse import urlencode, quote, parse_qsl, urlparse

import conf

# note: ensure the redirect url is whitelisted in the
# 'Allowed Return URLs' section under 'Web Settings' for your
# Security Profile on Amazon Developer Portal.
callback_url = 'http://{address}:{port}/amazon-login/authresponse/'.format(
    address=conf.ADDRESS, port=conf.PORT
)


class AmazonAlexaServiceLoginHandler(BaseHTTPRequestHandler):
    oauth2_url = 'https://www.amazon.com/ap/oa'
    oauth2_token_url = 'https://api.amazon.com/auth/o2/token'

    def do_GET(self):
        routes = {
            '/amazon-login/': self.handle_login,
            '/amazon-login/authresponse/': self.handle_callback,
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
            ('client_id', conf.ALEXA_VOICE_SERVICE_CLIENT_ID),
            ('scope', 'alexa:all'),
            ('scope_data', json.dumps({
                'alexa:all': OrderedDict([
                    ('productID', conf.ALEXA_VOICE_SERVICE_DEVICE_TYPE_ID),
                    ('productInstanceAttributes', {
                        'deviceSerialNumber': '001'
                    })
                ])
            })),
            ('response_type', 'code'),
            ('redirect_uri', callback_url)
        ])

        self.send_header(
            'Location', self.oauth2_url + '?' + urlencode(params)
        )
        self.end_headers()
        return

    def handle_callback(self):
        params = dict(parse_qsl(urlparse(self.path).query))
        payload = {
            'client_id': conf.ALEXA_VOICE_SERVICE_CLIENT_ID,
            'client_secret': conf.ALEXA_VOICE_SERVICE_CLIENT_SECRET,
            'code': quote(params['code']),
            'grant_type': 'authorization_code',
            'redirect_uri': callback_url,
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
