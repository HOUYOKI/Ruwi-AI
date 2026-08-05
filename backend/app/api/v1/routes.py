from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api.deps import current_user, require_roles
from app.ai.planner.service import ExperiencePlanner
from app.ai.providers.factory import ProviderFactory
from app.core.config import settings
from app.core.security import create_token, hash_password, verify_password, decode_token
from app.db.session import get_db
from app.models import *
from app.repositories.user_repository import UserRepository
from app.schemas.auth import *
from app.schemas.ai import ExperiencePlan
from app.services.artifact_service import artifact_dict
from app.services.storage_service import StorageService
router=APIRouter()

def audit(db,actor,action,etype,eid=None,details=None): db.add(AuditLog(actor_id=getattr(actor,"id",None),action=action,entity_type=etype,entity_id=eid,details=details or {}))
@router.get("/health")
def health(db:Session=Depends(get_db)): db.execute(__import__('sqlalchemy').text("SELECT 1")); return {"status":"ok","service":"ruwi-api","ai_provider":settings.ai_provider}
@router.post("/auth/register",response_model=TokenResponse,status_code=201)
def register(body:RegisterRequest,db:Session=Depends(get_db)):
    if UserRepository.by_email(db,body.email): raise HTTPException(409,detail={"code":"EMAIL_EXISTS","message":"An account with this email already exists"})
    role=db.query(Role).filter(Role.name=="visitor").one(); user=User(email=body.email.lower(),password_hash=hash_password(body.password),full_name=body.full_name,preferred_language=body.preferred_language,roles=[role]); db.add(user); db.commit(); db.refresh(user); return TokenResponse(access_token=create_token(user.id),refresh_token=create_token(user.id,"refresh"))
@router.post("/auth/login",response_model=TokenResponse)
def login(body:LoginRequest,db:Session=Depends(get_db)):
    user=UserRepository.by_email(db,body.email)
    if not user or not verify_password(body.password,user.password_hash): raise HTTPException(401,detail={"code":"INVALID_CREDENTIALS","message":"Invalid email or password"})
    return TokenResponse(access_token=create_token(user.id),refresh_token=create_token(user.id,"refresh"))
@router.post("/auth/refresh",response_model=TokenResponse)
def refresh(body:RefreshRequest):
    try: sub=decode_token(body.refresh_token,"refresh")["sub"]
    except ValueError: raise HTTPException(401,detail={"code":"INVALID_REFRESH_TOKEN","message":"Invalid or expired refresh token"})
    return TokenResponse(access_token=create_token(sub),refresh_token=create_token(sub,"refresh"))
@router.post("/auth/logout")
def logout(user=Depends(current_user)): return {"message":"Logged out. Remove tokens from the client."}
@router.post("/auth/password-reset/request")
def password_request(body:PasswordResetRequest): return {"message":"If the account exists, reset instructions have been generated."}
@router.post("/auth/password-reset/confirm")
def password_confirm(body:PasswordResetConfirm): return {"message":"Password reset token validation is available through the deployment mail adapter."}
@router.get("/auth/me",response_model=UserOut)
def me(user=Depends(current_user)): return UserOut(id=user.id,email=user.email,full_name=user.full_name,preferred_language=user.preferred_language,roles=[r.name for r in user.roles])
@router.patch("/profiles/me",response_model=UserOut)
def profile(body:ProfileUpdate,user=Depends(current_user),db:Session=Depends(get_db)):
    if body.full_name is not None:user.full_name=body.full_name
    if body.preferred_language in {"ar","en"}:user.preferred_language=body.preferred_language
    audit(db,user,"profile.updated","user",user.id); db.commit(); return me(user)
@router.get("/artifacts")
def artifacts(language:str="en",page:int=1,page_size:int=12,search:str="",category:str|None=None,db:Session=Depends(get_db)):
    q=db.query(Artifact).filter(Artifact.is_published.is_(True))
    if search:q=q.filter((Artifact.title_en.ilike(f"%{search}%"))|(Artifact.title_ar.ilike(f"%{search}%")))
    if category:q=q.join(ArtifactCategory).filter(ArtifactCategory.slug==category)
    total=q.count(); rows=q.order_by(Artifact.created_at.desc()).offset((page-1)*page_size).limit(min(page_size,50)).all(); return {"items":[artifact_dict(a,language,False) for a in rows],"total":total,"page":page,"page_size":page_size}
@router.get("/artifacts/{slug}")
def artifact(slug:str,language:str="en",db:Session=Depends(get_db)):
    a=db.query(Artifact).filter(Artifact.slug==slug).first()
    if not a: raise HTTPException(404,detail={"code":"ARTIFACT_NOT_FOUND","message":"Artifact not found"})
    result=artifact_dict(a,language,True); refs=db.query(ArtifactSourceReference,KnowledgeSource).join(KnowledgeSource,ArtifactSourceReference.source_id==KnowledgeSource.id).filter(ArtifactSourceReference.artifact_id==a.id).all(); result["sources"]=[{"label":r.citation_label,"title":s.title,"organization":s.organization,"trust_level":s.trust_level} for r,s in refs]; return result
@router.get("/categories")
def categories(language:str="en",db:Session=Depends(get_db)): return [{"id":x.id,"slug":x.slug,"name":x.name_ar if language=="ar" else x.name_en} for x in db.query(ArtifactCategory).filter(ArtifactCategory.enabled.is_(True)).all()]
@router.post("/uploads/artifact-image",status_code=201)
async def upload_image(file:UploadFile=File(...),user=Depends(current_user),db:Session=Depends(get_db)):
    path,mime,size,width,height=await StorageService.save_image(file); image=ArtifactImage(path=str(path),mime_type=mime,size_bytes=size,width=width,height=height); db.add(image); db.flush(); analysis=ArtifactAnalysis(user_id=user.id,image_id=image.id,status="queued",current_stage="queued",progress=0); db.add(analysis); audit(db,user,"artifact.uploaded","analysis",analysis.id); db.commit(); return {"analysis_id":analysis.id,"status":"queued"}
def process_analysis(analysis_id:str):
    from app.db.session import SessionLocal
    db=SessionLocal()
    try:
        a=db.get(ArtifactAnalysis,analysis_id)
        if not a:return
        a.status="failed";a.current_stage="failed";a.progress=100;a.started_at=datetime.utcnow();a.completed_at=datetime.utcnow();a.error_message="AI provider is not configured for real image analysis.";db.commit()
    finally:db.close()
@router.post("/analyses/{analysis_id}/start")
def start_analysis(analysis_id:str,tasks:BackgroundTasks,user=Depends(current_user),db:Session=Depends(get_db)):
    a=db.get(ArtifactAnalysis,analysis_id)
    if not a: raise HTTPException(404,detail={"code":"ANALYSIS_NOT_FOUND","message":"Analysis not found"})
    ProviderFactory.ensure_configured(); a.status="queued";a.current_stage="validating_image";a.progress=5;a.started_at=datetime.utcnow();db.commit();tasks.add_task(process_analysis,a.id);return {"id":a.id,"status":a.status,"stage":a.current_stage,"progress":a.progress}
@router.get("/analyses/{analysis_id}")
def analysis_status(analysis_id:str,user=Depends(current_user),db:Session=Depends(get_db)):
    a=db.get(ArtifactAnalysis,analysis_id)
    if not a: raise HTTPException(404,detail={"code":"ANALYSIS_NOT_FOUND","message":"Analysis not found"})
    return {"id":a.id,"status":a.status,"stage":a.current_stage,"progress":a.progress,"error_message":a.error_message,"retry_count":a.retry_count}
@router.post("/experience-plans",response_model=ExperiencePlan)
def experience_plan(metadata:dict,language:str="en",audience:str="general"): return ExperiencePlanner().plan(metadata,["verified context"],language,audience)
@router.post("/quizzes/{quiz_id}/attempts")
def quiz_attempt(quiz_id:str,answers:list[int],user=Depends(current_user),db:Session=Depends(get_db)):
    q=db.get(Quiz,quiz_id)
    if not q:raise HTTPException(404,detail={"code":"QUIZ_NOT_FOUND","message":"Quiz not found"})
    score=sum(1 for i,x in enumerate(q.questions) if i<len(answers) and answers[i]==x.correct_index); attempt=QuizAttempt(quiz_id=q.id,user_id=user.id,score=score,total=len(q.questions),answers=answers);db.add(attempt);db.commit();return {"score":score,"total":len(q.questions),"percentage":round(score/max(len(q.questions),1)*100)}
@router.get("/saved-experiences")
def saved(user=Depends(current_user),db:Session=Depends(get_db)): return [artifact_dict(a,user.preferred_language,False) for a in db.query(Artifact).join(SavedExperience).filter(SavedExperience.user_id==user.id).all()]
@router.post("/saved-experiences/{artifact_id}",status_code=201)
def save(artifact_id:str,user=Depends(current_user),db:Session=Depends(get_db)):
    if not db.get(Artifact,artifact_id):raise HTTPException(404,detail={"code":"ARTIFACT_NOT_FOUND","message":"Artifact not found"})
    if not db.query(SavedExperience).filter_by(user_id=user.id,artifact_id=artifact_id).first():db.add(SavedExperience(user_id=user.id,artifact_id=artifact_id));db.commit()
    return {"message":"Experience saved"}
@router.delete("/saved-experiences/{artifact_id}")
def unsave(artifact_id:str,user=Depends(current_user),db:Session=Depends(get_db)):
    db.query(SavedExperience).filter_by(user_id=user.id,artifact_id=artifact_id).delete();db.commit();return {"message":"Experience removed"}
@router.post("/conversations/{artifact_id}/messages")
def chat(artifact_id:str,body:dict,user=Depends(current_user),db:Session=Depends(get_db)):
    artifact=db.get(Artifact,artifact_id)
    if not artifact:raise HTTPException(404,detail={"code":"ARTIFACT_NOT_FOUND","message":"Artifact not found"})
    ProviderFactory.ensure_configured(); return {"answer":"","citations":[]}
@router.get("/curator/reviews")
def pending_reviews(user=Depends(require_roles("curator","admin")),db:Session=Depends(get_db)): return [artifact_dict(a,user.preferred_language,False) for a in db.query(Artifact).filter(Artifact.review_status.in_(["pending_review","changes_requested"])).all()]
@router.patch("/curator/artifacts/{artifact_id}")
def edit_artifact(artifact_id:str,body:dict,user=Depends(require_roles("curator","admin")),db:Session=Depends(get_db)):
    a=db.get(Artifact,artifact_id)
    if not a:raise HTTPException(404,detail={"code":"ARTIFACT_NOT_FOUND","message":"Artifact not found"})
    allowed={"title_ar","title_en","description_ar","description_en","review_status"}
    for k,v in body.items():
        if k in allowed:setattr(a,k,v)
    audit(db,user,"artifact.edited","artifact",a.id,{"fields":list(body)});db.commit();return artifact_dict(a,user.preferred_language,True)
@router.post("/curator/artifacts/{artifact_id}/review")
def review(artifact_id:str,body:dict,user=Depends(require_roles("curator","admin")),db:Session=Depends(get_db)):
    a=db.get(Artifact,artifact_id)
    if not a:raise HTTPException(404,detail={"code":"ARTIFACT_NOT_FOUND","message":"Artifact not found"})
    status=body.get("status")
    if status not in {"changes_requested","approved","rejected"}:raise HTTPException(422,detail={"code":"INVALID_REVIEW_STATUS","message":"Invalid review status"})
    a.review_status=status;db.add(CuratorReview(artifact_id=a.id,curator_id=user.id,status=status,section_statuses=body.get("sections",{}),notes=body.get("notes","")));audit(db,user,"artifact.reviewed","artifact",a.id,{"status":status});db.commit();return {"status":status}
@router.post("/curator/artifacts/{artifact_id}/publish")
def publish(artifact_id:str,user=Depends(require_roles("curator","admin")),db:Session=Depends(get_db)):
    a=db.get(Artifact,artifact_id)
    if not a or a.review_status!="approved":raise HTTPException(409,detail={"code":"APPROVAL_REQUIRED","message":"Artifact must be approved before publication"})
    version=db.query(PublicationRecord).filter_by(artifact_id=a.id).count()+1;a.review_status="published";a.is_published=True;db.add(PublicationRecord(artifact_id=a.id,published_by=user.id,version=version,snapshot=artifact_dict(a,"en",True)));audit(db,user,"artifact.published","artifact",a.id,{"version":version});db.commit();return {"status":"published","version":version}
@router.get("/admin/analytics")
def analytics(user=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    total=db.query(ArtifactAnalysis).count();successful=db.query(ArtifactAnalysis).filter_by(status="completed").count();failed=db.query(ArtifactAnalysis).filter_by(status="failed").count();return {"total_analyses":total,"successful_analyses":successful,"failed_analyses":failed,"published_artifacts":db.query(Artifact).filter_by(is_published=True).count(),"pending_reviews":db.query(Artifact).filter_by(review_status="pending_review").count(),"saved_experiences":db.query(SavedExperience).count(),"quiz_completions":db.query(QuizAttempt).count(),"users":db.query(User).count(),"language_usage":{"ar":db.query(User).filter_by(preferred_language="ar").count(),"en":db.query(User).filter_by(preferred_language="en").count()}}
@router.get("/admin/users")
def users(user=Depends(require_roles("admin")),db:Session=Depends(get_db)): return [{"id":x.id,"email":x.email,"full_name":x.full_name,"roles":[r.name for r in x.roles],"active":x.is_active} for x in db.query(User).all()]
@router.get("/admin/audit-logs")
def logs(user=Depends(require_roles("admin")),db:Session=Depends(get_db),limit:int=100): return [{"id":x.id,"action":x.action,"entity_type":x.entity_type,"entity_id":x.entity_id,"details":x.details,"created_at":x.created_at} for x in db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(min(limit,500)).all()]
@router.get("/admin/museums")
def museums(user=Depends(require_roles("admin")),db:Session=Depends(get_db)):return [{"id":x.id,"name_ar":x.name_ar,"name_en":x.name_en,"city":x.city} for x in db.query(Museum).all()]
@router.get("/knowledge/sources")
def sources(user=Depends(require_roles("curator","admin")),db:Session=Depends(get_db)):return [{"id":x.id,"title":x.title,"organization":x.organization,"language":x.language,"trust_level":x.trust_level,"verification_status":x.verification_status} for x in db.query(KnowledgeSource).all()]
