import hashlib
import hmac

import bcrypt

# Hash falso para igualar el tiempo de respuesta cuando el correo no existe
_DUMMY_HASH = bcrypt.hashpw(b"dummy-password", bcrypt.gensalt(rounds=12))

LEGACY_PREFIX = "pbkdf2_sha256$"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt(rounds=12)
    ).decode("utf-8")


def is_legacy_hash(password_hash: str) -> bool:
    return password_hash.startswith(LEGACY_PREFIX)


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        bcrypt.checkpw(password.encode("utf-8"), _DUMMY_HASH)  # iguala tiempos
        return False
    try:
        if is_legacy_hash(password_hash):
            _, iterations, salt_hex, digest_hex = password_hash.split("$")
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(iterations),
            )
            return hmac.compare_digest(digest.hex(), digest_hex)
        return bcrypt.checkpw(
            password.encode("utf-8"), password_hash.encode("utf-8")
        )
    except ValueError:
        return False