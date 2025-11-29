"""
encryption.py

This file contains a very simple "encryption" helper that both the client and
server can use. It is NOT secure for real-world use, but it is perfect
for learning how encrypted messages could be sent over a network.

We use a tiny XOR-based cipher:
- We take the text as bytes
- We XOR each byte with a repeating key
- Then we base64-encode the result so it can be sent as normal text

This allows us to:
- Encrypt a string into a weird-looking text
- Decrypt it back to the original
"""

import base64
from typing import Optional


# This is the "shared secret key" used for our XOR cipher.
# In a real application, keys must be protected carefully.
SECRET_KEY = "my_simple_key"


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    """
    Helper function that XORs each byte of 'data' with the bytes from 'key'.
    The key is repeated as many times as necessary.

    This is the "core" of the encryption and decryption.
    """
    result = bytearray()
    key_len = len(key)

    for index, byte in enumerate(data):
        key_byte = key[index % key_len]
        result.append(byte ^ key_byte)

    return bytes(result)


def encrypt_text(plain_text: str, key: Optional[str] = None) -> str:
    """
    Encrypt a string into a base64-encoded ciphertext string.

    Steps:
    1. Convert the plain text to bytes.
    2. XOR the bytes with the key bytes.
    3. Base64-encode the XOR'ed bytes so we can send them as text.

    Returns:
        A string that looks like random characters, but the server/client
        can turn back into the original message.
    """
    if key is None:
        key = SECRET_KEY

    plain_bytes = plain_text.encode("utf-8")
    key_bytes = key.encode("utf-8")

    xored = _xor_bytes(plain_bytes, key_bytes)
    encrypted = base64.b64encode(xored).decode("utf-8")
    return encrypted


def decrypt_text(cipher_text: str, key: Optional[str] = None) -> str:
    """
    Decrypt a base64-encoded ciphertext string back into the original text.

    Steps:
    1. Base64-decode the cipher text into XOR'ed bytes.
    2. XOR again with the same key (XOR twice = original).
    3. Decode the bytes back into a string.
    """
    if key is None:
        key = SECRET_KEY

    key_bytes = key.encode("utf-8")
    cipher_bytes = base64.b64decode(cipher_text.encode("utf-8"))

    xored_back = _xor_bytes(cipher_bytes, key_bytes)
    plain_text = xored_back.decode("utf-8")
    return plain_text
