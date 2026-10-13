from app.api.routes.departments import router as departments_router
from app.api.routes.employees import router as employees_router
from app.api.routes.health import router as health_router
from app.api.routes.roles import router as roles_router

__all__ = ["departments_router", "employees_router", "health_router", "roles_router"]
