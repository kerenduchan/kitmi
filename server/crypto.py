import os
from pathlib import Path
import cryptography.fernet

key_path = os.getenv("DB_PATH")
if key_path is None:
    key_path = "."

KEY_FILENAME = f'{key_path}/key.txt'


class Crypto:
    def __init__(self):
        self._key = None

    @staticmethod
    def generate_key():
        path = Path(KEY_FILENAME)
        if path.is_file():
            return

        print('Generating key')
        key = cryptography.fernet.Fernet.generate_key()
        with open(KEY_FILENAME, 'wb') as f:
            f.write(key)

    def encrypt(self, s):
        if self._key is None:
            self._load_key()

        f = cryptography.fernet.Fernet(self._key)
        return f.encrypt(bytes(s, 'utf-8')).decode('utf-8')

    def decrypt(self, s):
        if self._key is None:
            self._load_key()

        f = cryptography.fernet.Fernet(self._key)
        return f.decrypt(s).decode('utf-8')

    def _load_key(self):
        with open(KEY_FILENAME, 'rb') as f:
            self._key = f.read()
