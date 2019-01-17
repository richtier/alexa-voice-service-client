import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--client-id', help='AVS client ID', required=True)
parser.add_argument(
    '-s', '--client-secret', help='AVS client secret', required=True
)
parser.add_argument(
    '-d', '--device-type-id', help='AVS device type id', required=True
)
parser.add_argument('-a', '--address', default='localhost')
parser.add_argument('-p', '--port', default=9000, type=int)
