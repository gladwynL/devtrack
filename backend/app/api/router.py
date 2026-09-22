from fastapi import APIRouter

from app.api import auth, health, issues, memberships, projects, users

api_router = APIRouter()
api_router.include_router(health.router)

api_v1 = APIRouter(prefix="/api")
api_v1.include_router(auth.router)
api_v1.include_router(users.router)
api_v1.include_router(projects.router)
api_v1.include_router(memberships.router)
api_v1.include_router(issues.router)
api_router.include_router(api_v1)
