import os
from cryptography.fernet import Fernet


class Vault:
    def __init__(self, folder):
        path=folder/'secret.key'
        configured=os.environ.get('MARKETING_SECRET_KEY')
        if configured:
            key=configured.encode()
        else:
            try:
                with path.open('xb') as file: file.write(Fernet.generate_key())
                if os.name!='nt': path.chmod(0o600)
            except FileExistsError: pass
            key=path.read_bytes()
        self.cipher=Fernet(key)

    def encode(self, value):
        return 'encrypted:'+self.cipher.encrypt(value.encode()).decode() if value else ''

    def decode(self, value):
        return self.cipher.decrypt(value[10:].encode()).decode() if value.startswith('encrypted:') else value
