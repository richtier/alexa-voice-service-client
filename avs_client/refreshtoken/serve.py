import argparse

import os

import handlers, server


def serve_forever(address, port, client_id, client_secret, device_type_id):
    server_address = (address, port)
    http_server = server.AmazonLoginHttpServer(
        server_address=server_address,
        RequestHandlerClass=handlers.AmazonAlexaServiceLoginHandler,
        client_id=client_id,
        client_secret=client_secret,
        device_type_id=device_type_id,
    )
    print('running server on http://{}:{}'.format(*server_address))
    http_server.serve_forever()
 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--client-id', help='AVS client ID', required=True
    )
    parser.add_argument(
        '-s', '--client-secret', help='AVS client secret', required=True
    )
    parser.add_argument(
        '-d', '--device-type-id', help='AVS device type id', required=True
    )
    parser.add_argument('-a', '--address', default='localhost')
    parser.add_argument('-p', '--port', default=8000, type=int)
    args = parser.parse_args()

    serve_forever(
        address=args.address,
        port=args.port,
        client_id=args.client_id,
        client_secret=args.client_secret,
        device_type_id=args.device_type_id,
    )
