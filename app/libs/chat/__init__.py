from fastapi import APIRouter

internal_v1 = APIRouter(prefix="/api/v1")

from ...mods.chat import handler