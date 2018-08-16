from http.server import HTTPServer


class AmazonLoginHttpServer(HTTPServer):
    def __init__(
        self, client_id, client_secret, device_type_id, callback_url,
        *args, **kwargs
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.device_type_id = device_type_id
        self.callback_url = callback_url
        super().__init__(*args, **kwargs)
