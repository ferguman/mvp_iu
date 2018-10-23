from base64 import standard_b64encode, standard_b64decode

from nacl import secret

from config.private_key import nsk_b64

def encrypt(plain_text: 'binary string') -> 'b64 string':

    return standard_b64encode(secret.SecretBox(standard_b64decode(nsk_b64)).encrypt(plain_text))

def decrypt(b64_ciper_text) -> 'binary string':

    return secret.SecretBox(standard_b64decode(nsk_b64)).decrypt(standard_b64decode(b64_ciper_text))
