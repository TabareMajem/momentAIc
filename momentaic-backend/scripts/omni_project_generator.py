import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.agents.guerrilla.asset_factory_agent import asset_factory_agent
import structlog

# Convert logs to simple print
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(indent=2, sort_keys=True)
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

STARTUPS = [
    {
        "name": "BondQuests",
        "description": "Gamified relationship app for couples to build deeper connections.",
        "industry": "Consumer Social / Dating",
        "style": "nano_banana", # Colorful pop-art
        "product_type": "starter_pack"
    },
    {
        "name": "AgentForge",
        "description": "AI Operating System for building and deploying autonomous agents.",
        "industry": "Developer Tools / AI",
        "style": "cyberpunk", # High-tech, neon
        "product_type": "developer_kit"
    },
    {
        "name": "SymbioTask",
        "description": "AI Productivity suite that predicts your next task before you do.",
        "industry": "Productivity / SaaS",
        "style": "minimalist", # Clean, apple-esque
        "product_type": "neural_link_adapter" # Joke product
    },
    {
        "name": "Recall",
        "description": "Privacy-first memory layer for your digital life.",
        "industry": "Privacy / AI",
        "style": "retro", # 90s nostalgia
        "product_type": "memory_card"
    },
    {
        "name": "Clawdbot",
        "description": "Community moderation bot with attitude.",
        "industry": "Gaming / Discord",
        "style": "gamer", # RGB lighting style
        "product_type": "hardware_bot" 
    }
]

async def main():
    print("🌍 ORCHESTRATING OMNI-PROJECT ASSET GENERATION 🌍", flush=True)
    print("Target: 5 Startups")
    print("Engine: Gemini Image Gen 3 (Native)", flush=True)
    print("="*60, flush=True)

    results_map = {}

    for startup in STARTUPS:
        name = startup["name"]
        print(f"\n🏭 PROCESSING: {name}...", flush=True)
        
        try:
            # Generate Product Mockups
            assets = await asset_factory_agent.generate_batch(
                asset_type="product_mockup",
                count=3,
                visual_style="photorealistic-gemini", # Trigger Imagen path
                context=startup,
                product_type=startup["product_type"],
                target_store="Best Buy" if "AI" in startup["industry"] else "Target"
            )
            
            results_map[name] = assets
            print(f"✅ Generated {len(assets)} assets for {name}", flush=True)
            
            for a in assets:
                print(f"   - {a.concept['product_name']}: {a.image_url[:60]}...", flush=True)
                
        except Exception as e:
            print(f"❌ Failed to generate for {name}: {e}", flush=True)
            import traceback
            traceback.print_exc()

    print("\n" + "="*60, flush=True)
    print("🎉 OMNI-GENERATION COMPLETE", flush=True)
    print("="*60, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
