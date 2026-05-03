"""
LLM Client - Groq API wrapper
"""
import os
from typing import Optional


class LLMClient:
    """Groq LLM client for message composition"""
    
    def __init__(self):
        self.client = None
        self.model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    
    def _get_client(self):
        """Lazy initialization of Groq client"""
        if self.client is None:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment")
            
            from groq import Groq
            self.client = Groq(api_key=api_key)
        
        return self.client
    
    def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> Optional[str]:
        """
        Call LLM with system and user prompts
        Returns: Generated text or None on error
        """
        try:
            client = self._get_client()
            
            print(f"[LLM] Calling {self.model}...")
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            print(f"[LLM] Response received: {len(content)} chars")
            return content
        
        except Exception as e:
            print(f"[LLM] Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None


# Global client instance
llm_client = LLMClient()
