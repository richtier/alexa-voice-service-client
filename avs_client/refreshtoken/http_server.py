from http.server import HTTPServer


class AmazonLoginHttpServer(HTTPServer):
    def __init__(
        self, client_id, client_secret, device_type_id, *args, **kwargs
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.device_type_id = device_type_id
        super().__init__(*args, **kwargs)
