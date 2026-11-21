# LLM PS20 – Multi-turn Memory Chatbot

**Problem statement:** Basic bots forget earlier messages. This chatbot remembers the conversation, the user's name and their preferences within a session.

## How it works
- Full chat history is kept in `st.session_state` and sent to the LLM on every call (trimmed to the latest N messages).
- `memory.py` detects the user's name and preferences ("my name is…", "I like…") and injects them into the system prompt.
- The sidebar shows what the bot currently remembers; a button clears the memory.
- Uses any OpenAI-compatible API (Groq, Gemini, Ollama) via `.env`.

## How to run
```
pip install -r requirements.txt
cp .env.example .env      # then put your API key in .env
streamlit run app.py
```

## Memory test
1. "Hi, my name is Asha and I love cricket." 
2. "What's the capital of France?"
3. "What is my name and what do I like?" → the bot should answer Asha and cricket.

_Add 1–2 screenshots here._
