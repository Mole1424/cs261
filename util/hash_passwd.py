from sys import argv

import werkzeug.security

if __name__ == "__main__":
    for passwd in argv[1:]:
        print(passwd + "=" + werkzeug.security.generate_password_hash(passwd))
