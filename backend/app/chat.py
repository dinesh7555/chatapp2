from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.neo4j_db import neo4j_db
import uuid
from app.schemas import ChatMessageRequest
from datetime import datetime
from app.llm import call_llm

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/start")
def start_chat(current_user=Depends(get_current_user)):
    conversation_id = str(uuid.uuid4())

    query = """
    MERGE (u:User {id: $user_id})
    CREATE (c:Conversation {
        id: $conversation_id,
        created_at: datetime()
    })
    CREATE (u)-[:HAS_CONVERSATION]->(c)
    RETURN c.id AS conversation_id
    """

    result = neo4j_db.run_query(
        query,
        {
            "user_id": current_user.id,
            "conversation_id": conversation_id
        }
    )

    return {
        "conversation_id": result[0]["conversation_id"]
    }

@router.post("/message")
def send_message(
    data: ChatMessageRequest,
    current_user=Depends(get_current_user)
):
    # 1️⃣ Verify conversation belongs to user
    verify_query = """
    MATCH (u:User {id: $user_id})-[:HAS_CONVERSATION]->(c:Conversation {id: $conversation_id})
    RETURN c
    """

    verify_result = neo4j_db.run_query(
        verify_query,
        {
            "user_id": current_user.id,
            "conversation_id": data.conversation_id
        }
    )

    if not verify_result:
        return {"error": "Conversation not found or access denied"}

    # 2️⃣ Store user message
    user_message_query = """
    MATCH (c:Conversation {id: $conversation_id})
    CREATE (m:Message {
        role: "user",
        content: $content,
        timestamp: datetime()
    })
    CREATE (c)-[:HAS_MESSAGE]->(m)
    RETURN m
    """

    neo4j_db.run_query(
        user_message_query,
        {
            "conversation_id": data.conversation_id,
            "content": data.message
        }
    )
    # 3️⃣ Fetch recent chat history for context
    history_query = """
    MATCH (c:Conversation {id: $conversation_id})-[:HAS_MESSAGE]->(m)
    RETURN m.role AS role, m.content AS content
    ORDER BY m.timestamp ASC
    LIMIT 10
    """

    history = neo4j_db.run_query(
        history_query,
        {"conversation_id": data.conversation_id}
    )

    messages = [
        {"role": h["role"], "content": h["content"]}
        for h in history
    ]

    # 3️⃣  assistant response (LLM later)
    assistant_reply = call_llm(messages)

    assistant_message_query = """
    MATCH (c:Conversation {id: $conversation_id})
    CREATE (m:Message {
        role: "assistant",
        content: $content,
        timestamp: datetime()
    })
    CREATE (c)-[:HAS_MESSAGE]->(m)
    RETURN m
    """

    neo4j_db.run_query(
        assistant_message_query,
        {
            "conversation_id": data.conversation_id,
            "content": assistant_reply
        }
    )

    return {
        "user_message": data.message,
        "assistant_message": assistant_reply
    }


@router.get("/history/{conversation_id}")
def chat_history(
    conversation_id: str,
    current_user=Depends(get_current_user)
):
    # 1️⃣ Verify conversation belongs to user
    verify_query = """
    MATCH (u:User {id: $user_id})-[:HAS_CONVERSATION]->(c:Conversation {id: $conversation_id})
    RETURN c
    """

    verify_result = neo4j_db.run_query(
        verify_query,
        {
            "user_id": current_user.id,
            "conversation_id": conversation_id
        }
    )

    if not verify_result:
        return {"error": "Conversation not found or access denied"}

    # 2️⃣ Fetch messages
    history_query = """
    MATCH (c:Conversation {id: $conversation_id})-[:HAS_MESSAGE]->(m)
    RETURN m.role AS role, m.content AS content
    ORDER BY m.timestamp ASC
    """

    messages = neo4j_db.run_query(
        history_query,
        {"conversation_id": conversation_id}
    )

    return {
        "conversation_id": conversation_id,
        "messages": messages
    }
