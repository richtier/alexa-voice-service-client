import os
import sys

# solve import error when calling this script from project root.
sys.path.append(os.getcwd())

from alexa_client.refreshtoken import arg_parser, http_server, handlers  # NOQA


def serve_forever(address, port, client_id, client_secret, device_type_id):
    server_address = (address, port)
    # ensure the redirect url is whitelisted in the
    # 'Allowed Return URLs' section under 'Web Settings' for your
    # Security Profile on Amazon Developer Portal.
    callback_url = 'http://{}:{}/callback/'.format(*server_address)
    server = http_server.AmazonLoginHttpServer(
        server_address=server_address,
        RequestHandlerClass=handlers.AmazonAlexaServiceLoginHandler,
        client_id=client_id,
        client_secret=client_secret,
        device_type_id=device_type_id,
        callback_url=callback_url,
    )
    print('running server on http://{}:{}'.format(*server_address))
    server.serve_forever()


if __name__ == '__main__':
    args = arg_parser.parser.parse_args()
    serve_forever(
        address=args.address,
        port=args.port,
        client_id=args.client_id,
        client_secret=args.client_secret,
        device_type_id=args.device_type_id,
    )
