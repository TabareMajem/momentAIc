from typing import Dict, Any

def _format_ai_snapshot(self, snapshot: Dict[str, Any]) -> str:
    """
    Format OpenClaw AI snapshot into readable text.
    The snapshot contains a simplified DOM tree with 'ref' IDs.
    """
    if not snapshot:
            return "Empty Snapshot"
            
    # Helper to recursively build text
    # This is a basic implementation to get started
    # Real OpenClaw snapshots have value/attrs/children
    
    output = []
    
    def recurse(node, depth=0):
        if not isinstance(node, dict): return
        
        prefix = "  " * depth
        role = node.get("role", "element")
        name = node.get("name", "")
        value = node.get("value", "")
        ref = node.get("ref", "")
        
        line = f"{prefix}[{role}]"
        if name: line += f" {name}"
        if value: line += f" (Value: {value})"
        if ref: line += f" (Ref: {ref})"
        
        output.append(line)
        
        for child in node.get("children", []):
            recurse(child, depth + 1)
    
    # Snapshot root might be a list or dict
    if isinstance(snapshot, list):
            for item in snapshot:
                recurse(item)
    else:
            recurse(snapshot)
            
    return "\n".join(output)
