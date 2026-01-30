import asyncio
import sys
import structlog

# Add project root to path BEFORE imports
sys.path.append("/root/momentaic/momentaic-backend")

from app.services.llm_context import llm_context_service, LLMContextService

logger = structlog.get_logger()

def test_llm_generation():
    print("\n--- Testing LLM Context Generation ---")
    
    # 1. Test concise llms.txt
    print("Generating llms.txt...")
    txt = llm_context_service.generate_llms_txt()
    print(f"Length: {len(txt)} chars")
    
    assert "# MomentAIc" in txt
    assert "Sales Hunter" in txt
    assert "Elon Musk" in txt
    print("✅ Concise format verified")
    
    # 2. Test full llms-full.txt
    print("\nGenerating llms-full.txt...")
    full_txt = llm_context_service.generate_llms_full_txt()
    print(f"Length: {len(full_txt)} chars")
    
    assert "Full Documentation" in full_txt
    assert "**Capabilities (Tools):**" in full_txt
    # Check for a known tool
    assert "web_search" in full_txt
    print("✅ detailed format verified")
    
    # 3. Test JSON-LD
    print("\nGenerating JSON-LD...")
    json_ld = llm_context_service.generate_json_ld()
    assert json_ld["@type"] == "SoftwareApplication"
    assert len(json_ld["agents"]) > 5
    print("✅ JSON-LD verified")
    
    print("\n✅ LLM Optimization Verification: SUCCESS")

if __name__ == "__main__":
    test_llm_generation()
