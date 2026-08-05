from pydantic import BaseModel, EmailStr, Field
class RegisterRequest(BaseModel): email:EmailStr; password:str=Field(min_length=8); full_name:str=Field(min_length=2); preferred_language:str="ar"
class LoginRequest(BaseModel): email:EmailStr; password:str
class RefreshRequest(BaseModel): refresh_token:str
class TokenResponse(BaseModel): access_token:str; refresh_token:str; token_type:str="bearer"
class UserOut(BaseModel): id:str; email:EmailStr; full_name:str; preferred_language:str; roles:list[str]
class ProfileUpdate(BaseModel): full_name:str|None=None; preferred_language:str|None=None
class PasswordResetRequest(BaseModel): email:EmailStr
class PasswordResetConfirm(BaseModel): token:str; new_password:str=Field(min_length=8)
