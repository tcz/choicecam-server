from Crypto.PublicKey import RSA
from Crypto import Random
import os
import qrcode
from config import PRIVATE_KEY_FILE_PATH, PUBLIC_KEY_FILE_PATH, PUBLIC_KEY_BARE_FILE_PATH, PUBLIC_KEY_QR_CODE_FILE_PATH

if not os.path.isfile(PUBLIC_KEY_FILE_PATH) and \
   not os.path.isfile(PRIVATE_KEY_FILE_PATH) and \
   not os.path.isfile(PUBLIC_KEY_BARE_FILE_PATH) and \
   not os.path.isfile(PUBLIC_KEY_QR_CODE_FILE_PATH):

    random_generator = Random.new().read
    key = RSA.generate(2048, random_generator)
    private, public = key.exportKey(), key.publickey().exportKey()
    bare_public = public \
        .replace(b"\n", b"") \
        .replace(b"-----BEGIN PUBLIC KEY-----", b"") \
        .replace(b"-----END PUBLIC KEY-----", b"")

    with open(PRIVATE_KEY_FILE_PATH, 'wb') as private_file:
        private_file.write(private)
    with open(PUBLIC_KEY_FILE_PATH, 'wb') as public_file:
        public_file.write(public)
    with open(PUBLIC_KEY_BARE_FILE_PATH, 'wb') as bare_public_file:
        bare_public_file.write(bare_public)

    image = qrcode.make(bare_public)
    image.save(PUBLIC_KEY_QR_CODE_FILE_PATH)