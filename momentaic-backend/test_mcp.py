
try:
    import mcp
    print("MCP imported successfully")
    from mcp import ClientSession
    print("ClientSession imported")
except ImportError as e:
    print(f"MCP import failed: {e}")
