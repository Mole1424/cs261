import werkzeug.security
from sys import argv


if __name__ == '__main__':
    for passwd in argv[1:]:
        print(passwd + "=" + werkzeug.security.generate_password_hash(passwd))
