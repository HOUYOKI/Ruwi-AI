from pydantic import BaseModel
class MessageResponse(BaseModel): message:str
class Page(BaseModel): items:list; total:int; page:int; page_size:int
class ApiError(BaseModel): code:str; message:str; details:dict|list|None=None
