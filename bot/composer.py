"""
Message Composer - Core composition logic
"""
import json
import re
from typing import Dict, Any, Optional
from .storage import store
from .llm_client import llm_client
from .prompts import SYSTEM_PROMPT, build_user_prompt, build_reply_prompt


def compose_message(trigger_id: str) -> Optional[Dict[str, Any]]:
    """
    Compose a message for a given trigger
    Returns action dict or None if shouldn't send
    """
    
    print(f"[COMPOSE] Starting composition for trigger: {trigger_id}")
    
    # Get trigger context
    trigger = store.get("trigger", trigger_id)
    if not trigger:
        print(f"[COMPOSE] Trigger not found: {trigger_id}")
        return None
    
    # Get merchant context
    merchant_id = trigger.get("merchant_id")
    if not merchant_id:
        print(f"[COMPOSE] No merchant_id in trigger")
        return None
    
    merchant = store.get("merchant", merchant_id)
    if not merchant:
        print(f"[COMPOSE] Merchant not found: {merchant_id}")
        return None
    
    # Get category context
    category_slug = merchant.get("category_slug")
    if not category_slug:
        print(f"[COMPOSE] No category_slug in merchant")
        return None
    
    category = store.get("category", category_slug)
    if not category:
        print(f"[COMPOSE] Category not found: {category_slug}")
        return None
    
    print(f"[COMPOSE] All contexts loaded. Calling LLM...")
    
    # Get customer context if needed
    customer = None
    customer_id = trigger.get("customer_id")
    if customer_id:
        customer = store.get("customer", customer_id)
    
    # Build prompt
    user_prompt = build_user_prompt(category, merchant, trigger, customer)
    
    # Call LLM
    response = llm_client.complete(SYSTEM_PROMPT, user_prompt)
    if not response:
        print(f"[COMPOSE] LLM returned no response")
        return None
    
    print(f"[COMPOSE] LLM response received: {response[:100]}...")
    
    # Parse JSON response
    try:
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(response)
        
        body = result.get("body", "")
        cta = result.get("cta", "open_ended")
        rationale = result.get("rationale", "LLM-composed message")
        
        if not body:
            return None
        
        # Determine send_as
        send_as = "merchant_on_behalf" if customer else "vera"
        
        # Build action
        action = {
            "conversation_id": f"conv_{merchant_id}_{trigger_id}",
            "merchant_id": merchant_id,
            "customer_id": customer_id,
            "send_as": send_as,
            "trigger_id": trigger_id,
            "template_name": f"vera_{trigger.get('kind', 'generic')}_v1",
            "template_params": [body[:100], body[100:200], body[200:300]],  # Split for template
            "body": body,
            "cta": cta,
            "suppression_key": trigger.get("suppression_key", f"msg:{trigger_id}"),
            "rationale": rationale
        }
        
        return action
    
    except Exception as e:
        print(f"Compose error: {e}")
        return None


def handle_reply(conversation_id: str, merchant_id: str, merchant_message: str, 
                 conversation_history: list) -> Dict[str, Any]:
    """
    Handle merchant reply
    Returns: {action: "send"|"wait"|"end", body: "...", cta: "...", rationale: "..."}
    """
    
    # Get merchant context
    merchant = store.get("merchant", merchant_id)
    if not merchant:
        return {"action": "end", "rationale": "Merchant context not found"}
    
    # Build reply prompt
    prompt = build_reply_prompt(conversation_history, merchant_message, merchant)
    
    # Call LLM
    response = llm_client.complete(SYSTEM_PROMPT, prompt)
    if not response:
        return {"action": "end", "rationale": "LLM error"}
    
    # Parse response
    try:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(response)
        
        action = result.get("action", "send")
        
        if action == "send":
            return {
                "action": "send",
                "body": result.get("body", ""),
                "cta": result.get("cta", "open_ended"),
                "rationale": result.get("rationale", "Reply composed")
            }
        elif action == "wait":
            return {
                "action": "wait",
                "wait_seconds": result.get("wait_seconds", 3600),
                "rationale": result.get("rationale", "Waiting for merchant")
            }
        else:  # end
            return {
                "action": "end",
                "rationale": result.get("rationale", "Conversation ended")
            }
    
    except Exception as e:
        print(f"Reply error: {e}")
        return {"action": "end", "rationale": f"Parse error: {e}"}
