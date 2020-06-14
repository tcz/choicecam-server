import binascii
import os
import json
from providers import provider_factory

CONFIG_PATH = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config'))

PRIVATE_KEY_FILE_PATH           = os.path.join(CONFIG_PATH, 'server.key')
PUBLIC_KEY_FILE_PATH            = os.path.join(CONFIG_PATH, 'server.pub')
PUBLIC_KEY_BARE_FILE_PATH       = os.path.join(CONFIG_PATH, 'server.bare.pub')
PUBLIC_KEY_QR_CODE_FILE_PATH    = os.path.join(CONFIG_PATH, 'server.pub.png')
SYMMETRIC_KEY_FILE_PATH         = os.path.join(CONFIG_PATH, 'symmetric.key')
SYMMETRIC_KEY_INFO_FILE_PATH    = os.path.join(CONFIG_PATH, 'symmetric.keyinfo')
PROVIDER_DATA_FILE_PATH         = os.path.join(CONFIG_PATH, 'provider_data.json')
VIDEO_OUTPUT_PATH               = os.path.realpath(os.path.join(CONFIG_PATH, '../output'))
FONT_PATH                       = os.path.realpath(os.path.join(CONFIG_PATH, '../quicksand-500.ttf'))
PLAYLIST_FILE_PATH              = os.path.join(VIDEO_OUTPUT_PATH, "playlist.m3u8")

def has_config_for_streaming():
    return os.path.isfile(SYMMETRIC_KEY_FILE_PATH) and \
           os.path.isfile(PROVIDER_DATA_FILE_PATH)

def save_config_for_streaming(config_from_client):

    with open(SYMMETRIC_KEY_FILE_PATH, 'wb') as symmetric_key_file:
        symmetric_key_file.write(binascii.unhexlify(config_from_client['symmetric_key']))

    with open(SYMMETRIC_KEY_INFO_FILE_PATH, 'w') as symmetric_key_info_file:
        symmetric_key_info_file.write(SYMMETRIC_KEY_FILE_PATH + "\n" + SYMMETRIC_KEY_FILE_PATH)

    with open(PROVIDER_DATA_FILE_PATH, 'w') as provider_data_file:
        provider_data_file.write(json.dumps(config_from_client['provider_data']))


def provider_from_config():
    if not has_config_for_streaming():
        raise RuntimeError('No config for streaming found')

    with open(PROVIDER_DATA_FILE_PATH, 'r') as provider_data_file:
        provider_data = json.loads(provider_data_file.read())

    return provider_factory(provider_data)