# app/repositories/message_repo.py

from app.neo4j_db import neo4j_db

def create_message(conversation_id: str, role: str, content: str) -> int:
    query = """
    MATCH (c:Conversation {id: $conversation_id})
    CREATE (m:Message {
        role: $role,
        content: $content,
        timestamp: datetime()
    })
    CREATE (c)-[:HAS_MESSAGE]->(m)
    RETURN id(m) AS message_id
    """
    return neo4j_db.run_query(query, {
        "conversation_id": conversation_id,
        "role": role,
        "content": content
    })[0]["message_id"]


def get_recent_messages(conversation_id: str, limit: int = 10):
    query = """
    MATCH (c:Conversation {id: $conversation_id})-[:HAS_MESSAGE]->(m)
    RETURN m.role AS role, m.content AS content
    ORDER BY m.timestamp ASC
    LIMIT $limit
    """
    return neo4j_db.run_query(query, {
        "conversation_id": conversation_id,
        "limit": limit
    })


def count_user_messages(conversation_id: str) -> int:
    query = """
    MATCH (c:Conversation {id: $conversation_id})-[:HAS_MESSAGE]->(m {role:'user'})
    RETURN count(m) AS count
    """
    return neo4j_db.run_query(query, {
        "conversation_id": conversation_id
    })[0]["count"]


def get_initial_user_messages(conversation_id: str, limit: int = 3) -> list[str]:
    query = """
    MATCH (c:Conversation {id: $conversation_id})-[:HAS_MESSAGE]->(m {role:'user'})
    RETURN m.content AS content
    ORDER BY m.timestamp ASC
    LIMIT $limit
    """
    rows = neo4j_db.run_query(query, {
        "conversation_id": conversation_id,
        "limit": limit
    })
    return [r["content"] for r in rows]

def get_full_conversation_messages(conversation_id: str):
    query = """
    MATCH (c:Conversation {id: $conversation_id})-[:HAS_MESSAGE]->(m)
    RETURN m.role AS role, m.content AS content, m.timestamp AS timestamp
    ORDER BY m.timestamp ASC
    """
    return neo4j_db.run_query(query, {
        "conversation_id": conversation_id
    })
