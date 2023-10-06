import re


def validate_email(email: str) -> bool:
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(pattern, email) is None:
        return False
    else:
        return True


def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    else:
        return True
