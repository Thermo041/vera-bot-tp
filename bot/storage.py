"""
Context storage - in-memory store with version management
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


class ContextStore:
    """In-memory context storage with version control"""
    
    def __init__(self):
        # (scope, context_id) -> {version, payload, stored_at}
        self.contexts: Dict[Tuple[str, str], Dict[str, Any]] = {}
        
    def store(self, scope: str, context_id: str, version: int, payload: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Store context with version control
        Returns: (accepted, reason, current_version)
        """
        key = (scope, context_id)
        current = self.contexts.get(key)
        
        # Check version conflict
        if current and current["version"] >= version:
            return False, "stale_version", current["version"]
        
        # Store new version
        self.contexts[key] = {
            "version": version,
            "payload": payload,
            "stored_at": datetime.utcnow().isoformat() + "Z"
        }
        
        return True, None, version
    
    def get(self, scope: str, context_id: str) -> Optional[Dict[str, Any]]:
        """Get context payload by scope and ID"""
        key = (scope, context_id)
        ctx = self.contexts.get(key)
        return ctx["payload"] if ctx else None
    
    def get_all_by_scope(self, scope: str) -> Dict[str, Dict[str, Any]]:
        """Get all contexts for a scope"""
        result = {}
        for (s, cid), ctx in self.contexts.items():
            if s == scope:
                result[cid] = ctx["payload"]
        return result
    
    def count_by_scope(self) -> Dict[str, int]:
        """Count contexts by scope"""
        counts = {"category": 0, "merchant": 0, "customer": 0, "trigger": 0}
        for (scope, _), _ in self.contexts.items():
            if scope in counts:
                counts[scope] += 1
        return counts
    
    def clear(self):
        """Clear all contexts"""
        self.contexts.clear()


# Global store instance
store = ContextStore()
