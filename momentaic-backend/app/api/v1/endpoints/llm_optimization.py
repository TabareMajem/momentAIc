from fastapi import APIRouter, Response
from app.services.llm_context import llm_context_service

router = APIRouter()

@router.get("/llms.txt", response_class=Response)
async def get_llms_txt():
    """
    Get concise LLM documentation
    """
    content = llm_context_service.generate_llms_txt()
    return Response(content=content, media_type="text/plain")

@router.get("/llms-full.txt", response_class=Response)
async def get_llms_full_txt():
    """
    Get full LLM documentation
    """
    content = llm_context_service.generate_llms_full_txt()
    return Response(content=content, media_type="text/plain")

@router.get("/metadata")
async def get_metadata():
    """
    Get JSON-LD metadata for the platform
    """
    return llm_context_service.generate_json_ld()
