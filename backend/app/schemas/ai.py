from pydantic import BaseModel, Field
class VisionCandidate(BaseModel):
    possible_name:str; alternative_names:list[str]=[]; category:str|None=None; possible_culture:str|None=None; possible_region:str|None=None; possible_historical_period:str|None=None; possible_materials:list[str]=[]; visible_inscriptions:list[str]=[]; visible_symbols:list[str]=[]; visual_characteristics:list[str]=[]; confidence_score:float=Field(ge=0,le=1); uncertainty_notes:list[str]=[]; search_keywords:list[str]=[]
class VisionResult(BaseModel): identified:bool; candidates:list[VisionCandidate]; model_name:str; prompt_version:str
class ExperiencePlan(BaseModel): components:list[str]; skipped:dict[str,str]; language:str; audience:str
