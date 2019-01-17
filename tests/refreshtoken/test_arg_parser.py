from alexa_client.refreshtoken import arg_parser


def test_parser_defaults():
    args = arg_parser.parser.parse_args([
        '--device-type-id=device-type-id-here',
        '--client-id=client-id-here',
        '--client-secret=client-secret-here',
    ])

    assert args.address == 'localhost'
    assert args.port == 9000
    assert args.client_id == 'client-id-here'
    assert args.client_secret == 'client-secret-here'
    assert args.device_type_id == 'device-type-id-here'


def test_parser_explicit_address_port():
    args = arg_parser.parser.parse_args([
        '--device-type-id=device-type-id-here',
        '--client-id=client-id-here',
        '--client-secret=client-secret-here',
        '--address=thinger',
        '--port=8101',
    ])

    assert args.address == 'thinger'
    assert args.port == 8101
    assert args.client_id == 'client-id-here'
    assert args.client_secret == 'client-secret-here'
    assert args.device_type_id == 'device-type-id-here'
