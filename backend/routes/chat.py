# DEPRECATED: This routing file is superseded by backend/routes/generate.py.
# Preserved temporarily for backward compatibility tracking.
from fastapi import APIRouter
router = APIRouter()

@router.post("/chat")
def chat():
    return {"assistant": {"text": "Endpoint deprecated. Please hit /api/generate."}}
