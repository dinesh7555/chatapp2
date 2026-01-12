# app/chat.py

from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.schemas import ChatMessageRequest

from app.repositories.conversation_repo import (
    create_conversation,
    verify_conversation_owner,
    list_user_conversations
)
from app.repositories.message_repo import (
    create_message,
    get_recent_messages,
    get_full_conversation_messages
)
from app.repositories.topic_repo import (
    link_topics_to_message,
    fetch_topic_memory
)
from app.repositories.memory_repo import (
    store_embedding,
    fetch_semantic_memory
)

from app.services.llm_service import (
    get_chat_response,
    create_embedding_safe
)
from app.services.semantic_memory import (
    extract_and_clean_topics,
    recency_decay,
    build_knowledge_context,
    should_use_memory
)
from app.services.title_service import (
    should_generate_title,
    generate_and_update_title
)

from app.llm import extract_topics

router = APIRouter(prefix="/chat", tags=["Chat"])

# ─────────────────────────────────────────────
# 1️⃣ START CHAT
# ─────────────────────────────────────────────
@router.post("/start")
def start_chat(current_user=Depends(get_current_user)):
    return {
        "conversation_id": create_conversation(current_user.id)
    }


# ─────────────────────────────────────────────
# 2️⃣ SEND MESSAGE
# ─────────────────────────────────────────────
@router.post("/message")
def send_message(
    data: ChatMessageRequest,
    current_user=Depends(get_current_user)
):
    if not verify_conversation_owner(current_user.id, data.conversation_id):
        return {"error": "Conversation not found"}

    # Store user message
    user_msg_id = create_message(
        data.conversation_id, "user", data.message
    )

    # Embedding
    embedding = create_embedding_safe(data.message)
    if embedding:
        store_embedding(user_msg_id, embedding)

    # Topics
    raw_topics = extract_topics(data.message)
    topics = extract_and_clean_topics(raw_topics)
    link_topics_to_message(current_user.id, user_msg_id, topics)

    # Topic memory
    topic_memories = {
        t: fetch_topic_memory(
            current_user.id, t, user_msg_id, limit=3
        )
        for t in topics
    }

    # Semantic memory
    FINAL_THRESHOLD = 0.45
    semantic_texts = []
    if embedding:
        semantic_rows = fetch_semantic_memory(
            current_user.id, embedding, user_msg_id, k=5
        )
        scored = []
        for r in semantic_rows:
            score = r["score"] * recency_decay(r["timestamp"])
            if score > 0.45:
                scored.append((score, r["content"]))

        semantic_texts = [
            c for _, c in sorted(scored, reverse=True)[:3]
        ]

    # Build context
    knowledge_context = build_knowledge_context(
        topic_memories, semantic_texts
    )

    # Chat history
    history = get_recent_messages(data.conversation_id)
    messages = [
        {"role": h["role"], "content": h["content"]}
        for h in history
    ]

    system_prompt = (
        "You are a helpful AI assistant.\n"
            "Answer the user's question clearly and accurately."
            "Stay Strictly on the topic asked by the user"
            "Do NOT say phrases like 'previous discussions' or 'earlier conversations'."
    )

    if should_use_memory(topic_memories, semantic_texts):
        system_prompt += ("\n\n"
        + "The following is OPTIONAL reference information. "
        + "It is NOT part of the current conversation.\n"
        + "Use it only if directly relevant.\n\n"
        + knowledge_context
        )
    
    print("==============================================")
    print(topic_memories)
    print(semantic_texts)
    print("==============================================")
    print("SYSTEM PROMPT:\n", system_prompt)
    print("==============================================")
    # LLM call
    assistant_reply = get_chat_response(messages, system_prompt)

    # Store assistant reply
    create_message(
        data.conversation_id, "assistant", assistant_reply
    )

    # Title generation (ONCE)
    if should_generate_title(data.conversation_id):
        generate_and_update_title(data.conversation_id)

    return {
        "role": "assistant",
        "content": assistant_reply
    }


# ─────────────────────────────────────────────
# 3️⃣ CHAT HISTORY
# ─────────────────────────────────────────────
@router.get("/history/{conversation_id}")
def chat_history(
    conversation_id: str,
    current_user=Depends(get_current_user)
):
    if not verify_conversation_owner(current_user.id, conversation_id):
        return {"error": "Conversation not found"}

    messages = get_full_conversation_messages(conversation_id)

    return {
        "conversation_id": conversation_id,
        "messages": messages
    }


# ─────────────────────────────────────────────
# 4️⃣ LIST CONVERSATIONS
# ─────────────────────────────────────────────
@router.get("/conversations")
def list_conversations(current_user=Depends(get_current_user)):
    rows = list_user_conversations(current_user.id)

    return [
        {
            "conversation_id": r["conversation_id"],
            "title": r["title"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            "last_message_time": (
                r["last_message_time"].isoformat()
                if r["last_message_time"] else None
            )
        }
        for r in rows
    ]
