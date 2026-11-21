import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from memory import build_system_prompt, trim_history, update_profile

load_dotenv()

# Any OpenAI-compatible provider works. Defaults to Groq (free tier).
#   Groq   : https://api.groq.com/openai/v1            model: llama-3.3-70b-versatile
#   Gemini : https://generativelanguage.googleapis.com/v1beta/openai/   model: gemini-2.5-flash
#   Ollama : http://localhost:11434/v1  (api key can be "ollama")  model: llama3
API_KEY = os.getenv("LLM_API_KEY", "")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

st.set_page_config(page_title="Memory Chatbot", page_icon="🧠")
st.title("🧠 Multi-turn Memory Chatbot")
st.caption("Remembers the conversation, your name and your preferences within this session.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = {"name": "", "preferences": []}

with st.sidebar:
    st.header("What the bot remembers")
    st.write("**Name:**", st.session_state.profile["name"] or "—")
    st.write("**Preferences:**")
    for p in st.session_state.profile["preferences"] or ["—"]:
        st.write(f"- {p}")
    st.write(f"**Messages in memory:** {len(st.session_state.messages)}")
    max_msgs = st.slider("Max messages sent to LLM", 4, 40, 20, 2)
    if st.button("Clear memory / new chat"):
        st.session_state.messages = []
        st.session_state.profile = {"name": "", "preferences": []}
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not API_KEY:
    st.error("No API key found. Copy .env.example to .env and set LLM_API_KEY.")
    st.stop()

if user_text := st.chat_input("Say something, e.g. 'My name is Asha and I love cricket'"):
    update_profile(st.session_state.profile, user_text)
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    payload = [{"role": "system", "content": build_system_prompt(st.session_state.profile)}]
    payload += trim_history(st.session_state.messages, max_msgs)

    with st.chat_message("assistant"):
        try:
            client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
            stream = client.chat.completions.create(model=MODEL, messages=payload, stream=True)
            reply = st.write_stream(
                chunk.choices[0].delta.content or ""
                for chunk in stream if chunk.choices
            )
        except Exception as e:
            reply = f"⚠️ API error: {e}"
            st.error(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
