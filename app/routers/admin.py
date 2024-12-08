 # Routes spécifiques aux administrateurs
from fastapi import APIRouter

router = APIRouter()

@router.get("/admin/dashboard")
async def admin_dashboard():
    return {"message": "Welcome to the admin dashboard"}
