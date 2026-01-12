# app/services/title_service.py

from app.repositories.conversation_repo import (
    get_conversation_title,
    update_conversation_title
)
from app.repositories.message_repo import count_user_messages, get_initial_user_messages
from app.services.llm_service import generate_title_from_messages

def should_generate_title(conversation_id: str) -> bool:
    title = get_conversation_title(conversation_id)
    user_count = count_user_messages(conversation_id)

    return (
        (title is None or title == "New Chat")
        and user_count > 2
    )

def generate_and_update_title(conversation_id: str):
    user_texts = get_initial_user_messages(conversation_id, limit=3)
    title = generate_title_from_messages(user_texts)
    update_conversation_title(conversation_id, title)
