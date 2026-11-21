"""Helpers for the memory chatbot: profile extraction and prompt building.

Kept free of Streamlit/LLM imports so they are easy to unit test.
"""
import re

NAME_PATTERNS = [
    r"\bmy name is ([A-Za-z][A-Za-z'-]{1,29})",
    r"\bcall me ([A-Za-z][A-Za-z'-]{1,29})",
    r"\bi am ([A-Z][A-Za-z'-]{1,29})\b",
    r"\bi'm ([A-Z][A-Za-z'-]{1,29})\b",
]
PREF_PATTERNS = [
    r"\bi (?:really )?(?:like|love|enjoy|prefer) ([^.!?\n]+)",
    r"\bmy favou?rite ([^.!?\n]+)",
    r"\bplease (?:always )?(?:reply|answer|respond) ([^.!?\n]+)",
]
NOT_NAMES = {"a", "an", "the", "not", "so", "very", "fine", "good", "happy", "sad",
             "here", "ready", "student", "just", "also", "from", "in", "going"}


def update_profile(profile: dict, text: str) -> dict:
    """Look for a name and preferences in a user message and update the profile."""
    for pat in NAME_PATTERNS:
        m = re.search(pat, text, flags=re.IGNORECASE if "name is" in pat or "call me" in pat else 0)
        if m and m.group(1).lower() not in NOT_NAMES:
            profile["name"] = m.group(1).capitalize()
            break
    for pat in PREF_PATTERNS:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            pref = m.group(1).strip()
            if pref and pref not in profile["preferences"]:
                profile["preferences"].append(pref)
    return profile


def build_system_prompt(profile: dict) -> str:
    prompt = (
        "You are a friendly assistant with memory. Use the conversation history "
        "to stay consistent and answer follow-up questions. If the user asks what "
        "they told you earlier, answer from the history. Never invent facts about "
        "the user that they have not told you."
    )
    if profile.get("name"):
        prompt += f"\nThe user's name is {profile['name']}."
    if profile.get("preferences"):
        prompt += "\nKnown user preferences: " + "; ".join(profile["preferences"]) + "."
    return prompt


def trim_history(messages: list, max_messages: int = 20) -> list:
    """Keep only the latest messages so long chats stay within token limits."""
    return messages[-max_messages:]
