from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl, urlparse

import requests
from avs_client.refreshtoken import helpers


class AmazonAlexaServiceLoginHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.oauth2_manager = helpers.AmazonOauth2RequestManager(
            client_id=server.client_id,
            client_secret=server.client_secret,
        )
        super().__init__(request, client_address, server)

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
            self.send_response(404)
            self.end_headers()
            return
        return routes[path]()

    def handle_login(self):
        url = self.oauth2_manager.get_authorization_request_url(
            device_type_id=self.server.device_type_id,
            callback_url=self.callback_url,
        )
        self.send_response(302)
        self.send_header('Location', url)
        self.end_headers()
        return

    def handle_callback(self):
        params = dict(parse_qsl(urlparse(self.path).query))
        payload = self.oauth2_manager.get_authorizarization_grant_params(
            code=params['code'],
            callback_url=self.callback_url,
        )
        response = requests.post(
            self.oauth2_manager.authorization_grant_url, json=payload
        )
        if response.status_code != 200:
            self.send_response(response.status_code)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.content)
        else:
            self.send_response(response.status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            refresh_token = response.json()['refresh_token']
            self.wfile.write(bytes('refresh_token: ' + refresh_token, 'utf8'))
        return
