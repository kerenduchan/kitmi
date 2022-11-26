import cryptography.fernet

KEY_FILENAME = 'key.txt'


class Crypto:
    def __init__(self):
        self._key = None

    @staticmethod
    def generate_key():
        key = cryptography.fernet.Fernet.generate_key()
        with open(KEY_FILENAME, 'wb') as f:
            f.write(key)

    def encrypt(self, s):
        if self._key is None:
            self._load_key()

        f = cryptography.fernet.Fernet(self._key)
        return f.encrypt(s.encode())

    def decrypt(self, s):
        if self._key is None:
            self._load_key()

        f = cryptography.fernet.Fernet(self._key)
        return f.decrypt(s).decode()

    def _load_key(self):
        with open(KEY_FILENAME, 'rb') as f:
            self._key = f.read()
