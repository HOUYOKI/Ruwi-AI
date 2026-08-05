from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.db.session import get_db
from app.models import User
security=HTTPBearer(auto_error=False)
def current_user(credentials:HTTPAuthorizationCredentials=Depends(security),db:Session=Depends(get_db)):
    if not credentials: raise HTTPException(status_code=401,detail={"code":"AUTH_REQUIRED","message":"Authentication required"})
    try: payload=decode_token(credentials.credentials)
    except ValueError: raise HTTPException(status_code=401,detail={"code":"INVALID_TOKEN","message":"Invalid or expired token"})
    user=db.get(User,payload["sub"])
    if not user or not user.is_active: raise HTTPException(status_code=401,detail={"code":"USER_INACTIVE","message":"User is inactive"})
    return user
def require_roles(*allowed):
    def dep(user:User=Depends(current_user)):
        roles={r.name for r in user.roles}
        if not roles.intersection(allowed): raise HTTPException(status_code=403,detail={"code":"FORBIDDEN","message":"Insufficient permissions"})
        return user
    return dep
