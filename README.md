# Vera Bot - magicpin AI Challenge Submission

## Team Information
- **Team Name**: Team TP
- **Approach**: LLM-based message composer with context-aware prompting
- **Model**: Groq Llama 3.1 70B (FREE tier)

## Architecture

### Core Components
1. **Storage Layer** (`bot/storage.py`): In-memory context store with version management
2. **LLM Client** (`bot/llm_client.py`): Groq API wrapper
3. **Composer** (`bot/composer.py`): Message composition logic
4. **Prompts** (`bot/prompts.py`): Trigger-specific prompt templates
5. **API** (`bot/main.py`): FastAPI with 5 required endpoints

### Key Features
- ✅ Specificity: Uses real numbers from merchant context
- ✅ Category fit: Matches voice tone per business type
- ✅ Merchant fit: Personalizes with owner name, locality, offers
- ✅ Trigger relevance: Explains WHY NOW in every message
- ✅ Engagement: One clear CTA, low friction

## Local Setup

### Prerequisites
- Python 3.10+
- Groq API key (FREE from console.groq.com)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (already in .env)
# GROQ_API_KEY=your_key_here

# Run locally
python -m uvicorn bot.main:app --host 0.0.0.0 --port 8080
```

### Test Locally
```bash
# In another terminal
python judge_simulator.py
```

## Deployment (Render)

### Steps
1. Push code to GitHub
2. Connect Render to GitHub repo
3. Create new Web Service
4. Set environment variables in Render dashboard:
   - `GROQ_API_KEY`
   - `TEAM_NAME`
   - `TEAM_MEMBERS`
5. Deploy!

### Render Configuration
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn bot.main:app --host 0.0.0.0 --port $PORT`
- **Environment**: Python 3.10

## API Endpoints

- `GET /v1/healthz` - Health check
- `GET /v1/metadata` - Bot metadata
- `POST /v1/context` - Receive context updates
- `POST /v1/tick` - Generate messages
- `POST /v1/reply` - Handle merchant replies

## Scoring Strategy

### Target: 45+/50
- **Specificity (10)**: Real numbers from context
- **Category Fit (9)**: Voice matching per category
- **Merchant Fit (9)**: Owner name + locality + offers
- **Decision Quality (9)**: Clear trigger reasoning
- **Engagement (8)**: Strong CTA with low friction

## Design Decisions

1. **Groq over OpenAI**: FREE tier, faster, good quality
2. **In-memory storage**: Simple, fast, sufficient for challenge
3. **Single LLM call**: Minimizes latency (<5s per message)
4. **JSON output parsing**: Handles markdown code blocks
5. **Conversation history**: Tracks last 3 turns for context

## Tradeoffs

- **No Redis**: In-memory is fine for single instance
- **No retry logic**: Keeps code simple, relies on LLM reliability
- **Basic auto-reply detection**: Uses keyword matching in LLM prompt
- **No caching**: Each composition is fresh (better for adaptive context)

## Future Improvements

- Add Redis for multi-instance deployment
- Implement retry logic with exponential backoff
- Add more sophisticated auto-reply detection
- Cache category contexts (they change rarely)
- Add metrics/logging for production monitoring
