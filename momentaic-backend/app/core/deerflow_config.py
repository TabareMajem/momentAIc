import os

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "dummy_key_if_not_set")

DEERFLOW_CONFIG = {
    "models": [
        {
            "name": "deepseek-v3",
            "display_name": "DeepSeek V3",
            "use": "langchain_openai:ChatOpenAI",
            "model": "deepseek-chat",
            "base_url": "https://api.deepseek.com/v1",
            "api_key": DEEPSEEK_API_KEY,
            "max_tokens": 8192,
            "temperature": 0.6
        },
        {
            "name": "deepseek-r1",
            "display_name": "DeepSeek R1",
            "use": "langchain_openai:ChatOpenAI",
            "model": "deepseek-reasoner",
            "base_url": "https://api.deepseek.com/v1",
            "api_key": DEEPSEEK_API_KEY,
            "max_tokens": 32768,
            "temperature": 0.0
        }
    ],
    "default_model": "deepseek-v3"
}

def get_model_config(tier: str, byo_model: str = None) -> dict:
    """Returns the correct model config based on user tier and settings."""
    if byo_model and tier in ["growth", "god_mode"]:
        if byo_model == "gemini-3.0-flash":
             return {
                 "name": "gemini-3.0-flash",
                 "display_name": "Google Gemini 3.0 Flash",
                 "use": "langchain_google_genai:ChatGoogleGenerativeAI",
                 "model": "gemini-3.0-flash",
                 "api_key": os.getenv("GEMINI_API_KEY", "dummy"),
             }
        if byo_model == "seedance-2.0":
             # Mock example for Seedance
             return {
                 "name": "seedance-2.0",
                 "display_name": "Seedance 2.0 Video Gen",
                 "use": "custom:SeedanceAPI",
                 "model": "seedance-2",
                 "api_key": os.getenv("SEEDANCE_API_KEY", "dummy"),
             }
    
    if tier in ["growth", "god_mode"]:
        return next((m for m in DEERFLOW_CONFIG["models"] if m["name"] == "deepseek-r1"), {}) # type: ignore
    
    # Lite Tier uses DeepSeek V3 by default
    return next((m for m in DEERFLOW_CONFIG["models"] if m["name"] == "deepseek-v3"), {}) # type: ignore
