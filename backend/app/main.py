import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.routes import router
from app.core.config import settings
logging.basicConfig(level=settings.log_level)
logger=logging.getLogger("ruwi")
app=FastAPI(title="Ruwi API",version="1.0.0",debug=False,description="Bilingual AI-powered interactive museum platform")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_list,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.middleware("http")
async def security_headers(request:Request,call_next):
    response=await call_next(request);response.headers["X-Content-Type-Options"]="nosniff";response.headers["X-Frame-Options"]="DENY";response.headers["Referrer-Policy"]="strict-origin-when-cross-origin";return response
@app.exception_handler(RequestValidationError)
async def validation_handler(request,exc):return JSONResponse(status_code=422,content={"error":{"code":"VALIDATION_ERROR","message":"Request validation failed","details":exc.errors()}})
@app.exception_handler(Exception)
async def unhandled(request,exc):
    logger.exception("unhandled_error path=%s error_type=%s",request.url.path,type(exc).__name__)
    return JSONResponse(status_code=500,content={"error":{"code":"INTERNAL_ERROR","message":"An unexpected server error occurred"}})
app.include_router(router,prefix="/api/v1")
@app.get("/")
def root():return {"name":"Ruwi API","docs":"/docs","health":"/api/v1/health"}
