from fastapi import APIRouter
from server.services.config_manager import load_config, save_config

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/config")
async def get_config():
    return load_config()


@router.post("/config")
async def update_config(data: dict):
    return save_config(data)
