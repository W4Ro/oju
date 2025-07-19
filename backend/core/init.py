import secrets

def get_secret():
    charlist = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(charlist) for _ in range(64))