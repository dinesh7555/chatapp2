# app/services/llm_service.py

from app.llm import call_llm, call_llm_title, generate_embedding

def get_chat_response(messages: list, system_prompt: str) -> str:
    return call_llm(
        messages=messages,
        system_prompt=system_prompt
    )


def generate_title_from_messages(user_texts: list[str]) -> str:
    title = call_llm_title(user_texts)

    title = title.strip().split("\n")[0]
    title = title.replace('"', "").replace("'", "")
    title = " ".join(title.split()[:6])

    if not title or len(title) < 3:
        title = "New Chat"

    return title


def create_embedding_safe(text: str):
    try:
        return generate_embedding(text)
    except Exception as e:
        print("Embedding failed:", e)
        return None
