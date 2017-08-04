from http.server import HTTPServer


class AmazonLoginHttpServer(HTTPServer):
    def __init__(
        self, client_id, client_secret, device_type_id, *args, **kwargs
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.device_type_id = device_type_id
        super().__init__(*args, **kwargs)

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(
            request=request,
            client_address=client_address,
            server=self,
            client_id=self.client_id,
            client_secret=self.client_secret,
            device_type_id=self.device_type_id,
        )
