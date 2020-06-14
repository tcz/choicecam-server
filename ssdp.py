from ssdpy import SSDPServer
from config import PUBLIC_KEY_BARE_FILE_PATH

def run():
    with open(PUBLIC_KEY_BARE_FILE_PATH, 'r') as bare_public_file:
        public_key = bare_public_file.read()

    server = SSDPServer(public_key, device_type="ssdp:choicecam", port=1901)
    server.serve_forever()