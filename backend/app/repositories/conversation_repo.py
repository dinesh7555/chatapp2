

import uuid
from app.neo4j_db import neo4j_db


def create_conversation(user_id: int) -> str:
    """
    Create a new conversation node and link it to the user
    """
    conversation_id = str(uuid.uuid4())

    query = """
    MERGE (u:User {id: $user_id})
    CREATE (c:Conversation {
        id: $conversation_id,
        created_at: datetime(),
        title: "New Chat"
    })
    CREATE (u)-[:HAS_CONVERSATION]->(c)
    RETURN c.id AS conversation_id
    """

    result = neo4j_db.run_query(
        query,
        {
            "user_id": user_id,
            "conversation_id": conversation_id
        }
    )

    return result[0]["conversation_id"]


def verify_conversation_owner(user_id: int, conversation_id: str) -> bool:
    """
    Ensure the conversation belongs to the user
    """
    query = """
    MATCH (u:User {id: $user_id})-[:HAS_CONVERSATION]->(c:Conversation {id: $conversation_id})
    RETURN c
    """
    return bool(
        neo4j_db.run_query(
            query,
            {
                "user_id": user_id,
                "conversation_id": conversation_id
            }
        )
    )


def get_conversation_title(conversation_id: str) -> str | None:
    query = """
    MATCH (c:Conversation {id: $conversation_id})
    RETURN c.title AS title
    """
    result = neo4j_db.run_query(
        query,
        {"conversation_id": conversation_id}
    )
    return result[0]["title"] if result else None


def update_conversation_title(conversation_id: str, title: str):
    query = """
    MATCH (c:Conversation {id: $conversation_id})
    SET c.title = $title
    """
    neo4j_db.run_query(
        query,
        {
            "conversation_id": conversation_id,
            "title": title
        }
    )


def list_user_conversations(user_id: int):
    query = """
    MATCH (u:User {id: $user_id})-[:HAS_CONVERSATION]->(c:Conversation)
    OPTIONAL MATCH (c)-[:HAS_MESSAGE]->(m:Message)
    WITH c, max(m.timestamp) AS last_message_time
    RETURN
      c.id AS conversation_id,
      c.title AS title,
      c.created_at AS created_at,
      last_message_time
    ORDER BY last_message_time DESC
    """

    return neo4j_db.run_query(
        query,
        {"user_id": user_id}
    )
