"""
Asset Factory Agent
Automated factory for generating visual campaign assets at scale.

Orchestrates:
1. Concept Generation (via GuerrillaCampaignAgent)
2. Visual Prompt Engineering
3. Image Generation (via ImageService)
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import structlog
import asyncio

from app.services.image_service import image_service
from app.agents.guerrilla.guerrilla_campaign_agent import guerrilla_campaign_agent

logger = structlog.get_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class GeneratedAsset(BaseModel):
    """A complete generated asset with concept and visual"""
    asset_type: str
    concept: Dict[str, Any]
    image_url: str
    prompt_used: str
    status: str


# ═══════════════════════════════════════════════════════════════════════════════
# ASSET FACTORY AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class AssetFactoryAgent:
    """
    Asset Factory Agent - The "Scale" Engine
    
    Generates batches of visual assets by combining:
    - Text concepts (GuerrillaCampaignAgent)
    - Visual rendering (ImageService / DALL-E 3)
    """
    
    async def generate_batch(
        self,
        asset_type: str,
        count: int = 5,
        visual_style: str = "nano_banana",
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[GeneratedAsset]:
        """
        Generate a batch of assets (Concept + Image).
        
        Args:
            asset_type: product_mockup, parking_ticket
            count: Number of assets to generate
            visual_style: nano_banana, realistic, manga
            context: Startup context dict (name, description, industry, etc.)
            
        Returns:
            List of generated assets
        """
        startup_name = context.get("name", "Unknown Startup") if context else "BondQuests"
        logger.info(f"Asset Factory starting batch: {count} {asset_type}s for {startup_name}")
        
        results = []
        
        # 1. Generate Concepts
        concepts = []
        if asset_type == "product_mockup":
            # Generate varied concepts
            for _ in range(count):
                concept = await guerrilla_campaign_agent.generate_product_mockup_concept(
                    style=visual_style,
                    context=context,
                    **kwargs
                )
                concepts.append(concept)
                
        elif asset_type == "parking_ticket":
            # Generate varied tickets
            ticket_batch = await guerrilla_campaign_agent.generate_ticket_batch(count=count)
            concepts = ticket_batch
            
        else:
            logger.error(f"Unknown asset type: {asset_type}")
            return []
            
        # 2. Render Images (Parallel)
        tasks = []
        for concept in concepts:
            tasks.append(self._render_asset(asset_type, concept, visual_style))
            
        generated = await asyncio.gather(*tasks)
        
        # Filter successful generations
        results = [res for res in generated if res]
        
        logger.info(f"Asset Factory completed: {len(results)}/{count} assets")
        return results

    async def _render_asset(
        self,
        asset_type: str,
        concept: Any,
        style: str,
    ) -> Optional[GeneratedAsset]:
        """
        Render a single asset using DALL-E 3.
        """
        try:
            # Build Image Prompt
            prompt = self._build_image_prompt(asset_type, concept, style)
            
            # Generate Image
            image_result = await image_service.generate_image(
                prompt=prompt,
                style=style 
            )
            
            if image_result["status"] == "success":
                concept_dict = concept.model_dump() if hasattr(concept, 'model_dump') else concept.__dict__
                
                return GeneratedAsset(
                    asset_type=asset_type,
                    concept=concept_dict,
                    image_url=image_result["url"],
                    prompt_used=prompt,
                    status="success"
                )
            else:
                logger.error(f"Image generation failed: {image_result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"Asset rendering failed: {str(e)}")
            return None

    def _build_image_prompt(self, asset_type: str, concept: Any, style: str) -> str:
        """Construct a high-fidelity DALL-E 3 prompt."""
        
        base_style = "High-quality, photorealistic product photography, professional lighting, 4k."
        if style == "nano_banana":
            base_style = "Bright, colorful pop-art aesthetic, 'Nano Banana' brand style, playful high-contrast colors."
        elif style == "manga":
            base_style = "Black and white manga style, screentones, dramatic shading."
            
        if asset_type == "product_mockup":
            return f"""
{base_style}
A retail store shelf ({concept.store_setting}).
Focus on a specific product box: "{concept.product_name}".
Tagline on box: "{concept.tagline}".
Visuals on box: {concept.visual_description}.
The box should look like a real physical product sitting on the shelf next to other items.
Clear text, sleek packaging design.
"""

        elif asset_type == "parking_ticket":
            return f"""
{base_style}
Close-up photo of a fake parking ticket on a car windshield wiper.
The ticket is styled exactly like a real city parking citation but with humorous text.
Header says: "RELATIONSHIP CITATION".
Violation Code: "{concept.violation_code}".
Violation: "{concept.violation_type}".
Fine: "{concept.fine}".
High detail, legible text, realistic paper texture, natural outdoor lighting.
"""
        
        return ""


# Singleton instance
asset_factory_agent = AssetFactoryAgent()
