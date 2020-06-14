import binascii
import os, random, struct
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_file(key_filename, in_filename, out_filename):
    chunksize = 64 * 1024

    with open(key_filename, 'rb') as key_file:
        key = key_file.read(16)

    iv = get_random_bytes(16)

    encryptor = AES.new(key, AES.MODE_CBC, iv)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(binascii.hexlify(iv))
            outfile.write( b"\0\0\0\0")

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b"\0" * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))