import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.agents.guerrilla.asset_factory_agent import asset_factory_agent
import structlog

# Convert logs to simple print for script output
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(indent=2, sort_keys=True)
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

async def main():
    print("🚀 Starting Asset Factory Batch Generation...", flush=True)
    print("target: Product Mockups (Trojan Horse)", flush=True)
    print("style: High-Fidelity Photorealistic (DALL-E 3)", flush=True)

    try:
        # Generate 3 mockups
        print("\n--- Generating Product Mockups ---", flush=True)
        mockups = await asset_factory_agent.generate_batch(
            asset_type="product_mockup",
            count=3,
            visual_style="photorealistic", # Defaults to high-quality base prompt
            product_type="starter_pack",
            target_store="Target"
        )
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return

    print(f"\n✅ Generated {len(mockups)} Mockups:", flush=True)
    for m in mockups:
        print(f"\n[MOCKUP] {m.concept['product_name']}")
        print(f"Tagline: {m.concept['tagline']}")
        print(f"Angle: {m.concept['reddit_caption']}")
        print(f"Image URL: {m.image_url}")
        print(f"Prompt: {m.prompt_used[:100]}...")

    # Generate 3 parking tickets
    print("\n--- Generating Parking Tickets ---")
    tickets = await asset_factory_agent.generate_batch(
        asset_type="parking_ticket",
        count=3,
        visual_style="photorealistic"
    )

    print(f"\n✅ Generated {len(tickets)} Tickets:")
    for t in tickets:
        print(f"\n[TICKET] {t.concept['violation_type']}")
        print(f"Fine: {t.concept['fine']}")
        print(f"Image URL: {t.image_url}")

if __name__ == "__main__":
    asyncio.run(main())
