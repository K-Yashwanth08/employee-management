from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import departments_router, employees_router, health_router, roles_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")
WEB_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": str(exc.status_code), "message": str(exc.detail)}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(
            {"error": {"code": "422", "message": "Validation failed", "details": exc.errors()}}
        ),
    )


@app.get("/")
def root():
    return FileResponse(WEB_DIR / "index.html")

app.include_router(health_router)
app.include_router(departments_router)
app.include_router(roles_router)
app.include_router(employees_router)
