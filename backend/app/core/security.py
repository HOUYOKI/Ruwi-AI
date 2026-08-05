import base64, hashlib, hmac, json, os
from datetime import datetime, timedelta, timezone
from app.core.config import settings

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))

def hash_password(value: str) -> str:
    salt=os.urandom(16); iterations=310_000
    digest=hashlib.pbkdf2_hmac("sha256",value.encode(),salt,iterations)
    return f"pbkdf2_sha256${iterations}${_b64(salt)}${_b64(digest)}"

def verify_password(value: str, hashed: str) -> bool:
    try:
        scheme, rounds, salt, expected=hashed.split("$",3)
        if scheme!="pbkdf2_sha256": return False
        digest=hashlib.pbkdf2_hmac("sha256",value.encode(),_unb64(salt),int(rounds))
        return hmac.compare_digest(_b64(digest),expected)
    except (ValueError,TypeError): return False

def create_token(subject: str, kind: str="access") -> str:
    delta=timedelta(minutes=settings.access_token_expire_minutes) if kind=="access" else timedelta(days=settings.refresh_token_expire_days)
    header={"alg":"HS256","typ":"JWT"}; payload={"sub":subject,"type":kind,"exp":int((datetime.now(timezone.utc)+delta).timestamp())}
    signing=f"{_b64(json.dumps(header,separators=(',',':')).encode())}.{_b64(json.dumps(payload,separators=(',',':')).encode())}"
    sig=hmac.new(settings.jwt_secret.encode(),signing.encode(),hashlib.sha256).digest()
    return f"{signing}.{_b64(sig)}"

def decode_token(token: str, expected_type: str="access") -> dict:
    try:
        head,payload,sig=token.split(".")
        expected=hmac.new(settings.jwt_secret.encode(),f"{head}.{payload}".encode(),hashlib.sha256).digest()
        if not hmac.compare_digest(expected,_unb64(sig)): raise ValueError("Invalid signature")
        data=json.loads(_unb64(payload))
        if data.get("type")!=expected_type or int(data.get("exp",0))<int(datetime.now(timezone.utc).timestamp()): raise ValueError("Invalid or expired token")
        return data
    except Exception as exc:
        raise ValueError("Invalid or expired token") from exc
