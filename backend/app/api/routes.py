from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "running",
        "system": "Main Core AI Engineer",
        "author": "Budi Cahyono"
    }