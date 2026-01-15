from typing import Any, List
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
import os
import structlog

from app.core import security
from app.services.deliverable_service import deliverable_service, VAULT_DIR
from app.core.config import settings

router = APIRouter()
logger = structlog.get_logger()

class VaultFile(BaseModel):
    filename: str
    url: str
    size: int
    created_at: str
    type: str  # PDF, CSV, DOCX

@router.get("/", response_model=List[VaultFile])
async def get_vault_files(
    current_user: Any = Depends(security.get_current_user),
) -> Any:
    """
    List all generated deliverables in the vault.
    """
    files = []
    if os.path.exists(VAULT_DIR):
        for f in os.listdir(VAULT_DIR):
            path = os.path.join(VAULT_DIR, f)
            if os.path.isfile(path):
                stats = os.stat(path)
                file_type = "UNKNOWN"
                if f.endswith(".pdf"): file_type = "PDF"
                elif f.endswith(".csv"): file_type = "CSV"
                elif f.endswith(".docx"): file_type = "DOCX"
                elif f.endswith(".txt"): file_type = "TXT"
                
                files.append({
                    "filename": f,
                    "url": f"/static/vault/{f}",
                    "size": stats.st_size,
                    "created_at": str(stats.st_mtime),
                    "type": file_type
                })
    
    # Sort by newest
    files.sort(key=lambda x: x["created_at"], reverse=True)
    return files

@router.post("/generate-pack")
async def generate_day_one_pack(
    background_tasks: BackgroundTasks,
    current_user: Any = Depends(security.get_current_user),
) -> Any:
    """
    Trigger generation of the Day 1 Bundle.
    """
    # We use a background task to not block the UI
    background_tasks.add_task(
        deliverable_service.generate_day_one_pack,
        company_name=current_user.startup_name or "My Startup",
        industry=current_user.industry or "Technology"
    )
    
    return {"status": "generating", "message": "Day 1 Pack generation started. Files will appear in The Vault shortly."}
