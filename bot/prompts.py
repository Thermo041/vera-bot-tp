"""
Prompt templates for message composition
"""

SYSTEM_PROMPT = """You are Vera, magicpin's AI assistant for merchant growth in India.

YOUR ROLE: Compose WhatsApp messages that help merchants improve their business.

CRITICAL RULES:
1. SPECIFICITY: Use REAL numbers from context (views, CTR, dates, prices). Never invent data.
2. CATEGORY FIT: Match the business voice:
   - Dentists: Clinical, peer-to-peer, use "Dr." prefix
   - Salons: Warm, friendly, practical
   - Restaurants: Operator-to-operator
   - Gyms: Coaching, motivational
   - Pharmacies: Trustworthy, precise
3. MERCHANT FIT: Use owner's first name, locality, actual offers from their catalog
4. TRIGGER RELEVANCE: Explain WHY NOW - what triggered this message
5. ENGAGEMENT: One clear CTA, low friction, actionable

LANGUAGE:
- Hindi-English code-mix is natural and preferred
- Match merchant's language preference
- Use merchant's owner first name when available

OUTPUT FORMAT (JSON):
{
  "body": "The WhatsApp message text",
  "cta": "open_ended" or "binary_yes_no" or "none",
  "rationale": "One sentence explaining your composition choices"
}

NEVER:
- Fabricate data not in context
- Use promotional hype tone
- Make medical/legal claims
- Send generic "increase your sales" messages
"""


def build_user_prompt(category: dict, merchant: dict, trigger: dict, customer: dict = None) -> str:
    """Build user prompt from contexts"""
    
    # Extract key info
    cat_slug = category.get("slug", "unknown")
    cat_voice = category.get("voice", {})
    cat_offers = category.get("offer_catalog", [])[:3]  # Top 3 offers
    cat_peer_stats = category.get("peer_stats", {})
    
    merchant_id = merchant.get("merchant_id", "unknown")
    identity = merchant.get("identity", {})
    owner_name = identity.get("owner_first_name", identity.get("name", ""))
    merchant_name = identity.get("name", "")
    locality = identity.get("locality", "")
    city = identity.get("city", "")
    languages = identity.get("languages", ["en"])
    
    performance = merchant.get("performance", {})
    offers = merchant.get("offers", [])
    active_offers = [o for o in offers if o.get("status") == "active"]
    signals = merchant.get("signals", [])
    customer_agg = merchant.get("customer_aggregate", {})
    
    trigger_kind = trigger.get("kind", "unknown")
    trigger_payload = trigger.get("payload", {})
    trigger_urgency = trigger.get("urgency", 1)
    
    # Build digest info if research_digest
    digest_info = ""
    if trigger_kind == "research_digest":
        digest_items = category.get("digest", [])
        top_item_id = trigger_payload.get("top_item_id")
        if top_item_id:
            for item in digest_items:
                if item.get("id") == top_item_id:
                    digest_info = f"\nDIGEST ITEM: {item.get('title')} - {item.get('source')} - {item.get('summary', '')}"
                    break
    
    # Customer info if present
    customer_info = ""
    if customer:
        cust_identity = customer.get("identity", {})
        cust_name = cust_identity.get("name", "")
        cust_lang = cust_identity.get("language_pref", "english")
        cust_relationship = customer.get("relationship", {})
        cust_state = customer.get("state", "unknown")
        cust_prefs = customer.get("preferences", {})
        
        customer_info = f"""
CUSTOMER CONTEXT (send_as: merchant_on_behalf):
- Name: {cust_name}
- Language: {cust_lang}
- State: {cust_state}
- Last visit: {cust_relationship.get('last_visit', 'unknown')}
- Visits total: {cust_relationship.get('visits_total', 0)}
- Preferred slots: {cust_prefs.get('preferred_slots', 'unknown')}
"""
    
    prompt = f"""COMPOSE A MESSAGE FOR THIS MERCHANT:

CATEGORY: {cat_slug}
Voice tone: {cat_voice.get('tone', 'professional')}
Taboo words: {', '.join(cat_voice.get('vocab_taboo', [])[:3])}
Peer avg CTR: {cat_peer_stats.get('avg_ctr', 'unknown')}
Category offers: {', '.join([o.get('title', '') for o in cat_offers])}
{digest_info}

MERCHANT:
- Name: {merchant_name}
- Owner: {owner_name}
- Location: {locality}, {city}
- Languages: {', '.join(languages)}
- Performance: views={performance.get('views', '?')}, calls={performance.get('calls', '?')}, CTR={performance.get('ctr', '?')}
- Active offers: {', '.join([o.get('title', 'none') for o in active_offers]) if active_offers else 'none'}
- Signals: {', '.join(signals[:3])}
- Customer aggregate: {customer_agg}

TRIGGER:
- Kind: {trigger_kind}
- Urgency: {trigger_urgency}/5
- Payload: {trigger_payload}
{customer_info}

COMPOSE THE MESSAGE NOW. Return ONLY valid JSON with body, cta, and rationale fields.
"""
    
    return prompt


def build_reply_prompt(conversation_history: list, merchant_message: str, merchant: dict) -> str:
    """Build prompt for replying to merchant"""
    
    identity = merchant.get("identity", {})
    owner_name = identity.get("owner_first_name", "")
    
    history_text = "\n".join([
        f"{'VERA' if turn['from'] == 'vera' else 'MERCHANT'}: {turn['body']}"
        for turn in conversation_history[-3:]  # Last 3 turns
    ])
    
    prompt = f"""CONVERSATION SO FAR:
{history_text}

MERCHANT JUST SAID: "{merchant_message}"

ANALYZE THE MERCHANT'S MESSAGE:
1. Is it an auto-reply? (Look for "Thank you for contacting", "Our team will respond", etc.)
2. Is it explicit commitment? ("Yes", "Let's do it", "Go ahead")
3. Is it hostile/opt-out? ("Stop", "Not interested", "Don't message")
4. Is it a question or clarification?

RESPOND APPROPRIATELY:
- If auto-reply (2nd time): {{"action": "wait", "wait_seconds": 14400, "rationale": "..."}}
- If auto-reply (3rd time): {{"action": "end", "rationale": "..."}}
- If commitment: Switch to ACTION mode, provide next concrete step
- If hostile: {{"action": "end", "rationale": "..."}}
- If question: Answer and advance conversation

Return JSON with: {{"action": "send"|"wait"|"end", "body": "...", "cta": "...", "rationale": "..."}}
"""
    
    return prompt
