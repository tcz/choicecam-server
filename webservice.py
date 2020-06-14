import http.server
import socketserver
import traceback
from io import BytesIO
import base64
import json
import os
import sys
from Crypto.Cipher import PKCS1_v1_5
from providers import provider_factory
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from config import PRIVATE_KEY_FILE_PATH, save_config_for_streaming

PORT = 8000

class WebServiceHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    private_key = None

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            message = self.decrypt_body(body)
            provider = provider_factory(message['provider_data'])

            if not provider.credentials_correct():
                self.send_signed_response(400, b"Incorrect credentials")
                return

            save_config_for_streaming(message)

            base_path = provider.base_path()
            self.send_signed_response(200, base_path.encode())

            # Configuration no longer needed, shutting down server.
            sys.exit(0)
        except Exception as e:
            print(e, file=sys.stderr)
            traceback.print_exc()
            self.send_signed_response(500, b"Unknown error")

    def decrypt_body(self, body):
        if self.private_key is None:
            self.init_private_key()

        encrypted_message = base64.b64decode(body)
        cipher = PKCS1_v1_5.new(self.private_key)
        decrypted_message = cipher.decrypt(encrypted_message, None)

        return json.loads(decrypted_message)

    def init_private_key(self):
        with open(PRIVATE_KEY_FILE_PATH, 'r') as file:
            private_key = file.read()

        self.private_key = RSA.importKey(private_key)

    def send_signed_response(self, status_code, body):
        if self.private_key is None:
            self.init_private_key()

        hash = SHA.new()
        hash.update(body)
        signer = PKCS1_PSS.new(self.private_key)
        signature = signer.sign(hash)

        self.send_response(status_code)
        self.send_header("Signature", base64.b64encode(signature).decode("utf-8"))
        self.end_headers()

        response = BytesIO()
        response.write(body)
        self.wfile.write(response.getvalue())

def run():
    if not os.path.isfile(PRIVATE_KEY_FILE_PATH):
        raise RuntimeError('Server private key not found under ' + PRIVATE_KEY_FILE_PATH)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), WebServiceHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except:
            httpd.server_close()
            raise

