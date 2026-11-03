import bcrypt


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Compara una contraseña en texto plano contra un hash bcrypt almacenado."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def hash_password(plain_password: str) -> str:
    """Genera un hash bcrypt para almacenar contraseñas de forma segura."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
