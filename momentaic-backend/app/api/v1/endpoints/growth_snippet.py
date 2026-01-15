
class CampaignGenerateRequest(BaseModel):
    template_id: str
    template_name: str

@router.post("/campaigns/generate")
async def generate_campaign(
    request: CampaignGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a custom campaign plan using the Marketing Agent.
    Replaces static templates with AI-generated strategy.
    """
    from app.agents.marketing_agent import marketing_agent
    from app.models.startup import Startup
    
    # 1. Fetch User's Startup Context
    # (Assuming user has one active startup for this MVP, or we pick the first)
    result = await db.execute(select(Startup).where(Startup.user_id == current_user.id))
    startups = result.scalars().all()
    
    if not startups:
        startup_context = {"name": "My New Startup", "description": "A revolutionary new product."}
    else:
        s = startups[0]
        startup_context = {
            "name": s.name,
            "description": s.description,
            "industry": s.industry,
            "tagline": s.tagline
        }
        
    # 2. Agent Generation
    plan = await marketing_agent.generate_campaign_plan(
        template_name=request.template_name,
        startup_context=startup_context
    )
    
    return plan
