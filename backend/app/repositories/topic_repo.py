# app/repositories/topic_repo.py

from app.neo4j_db import neo4j_db


def link_topics_to_message(
    user_id: int,
    message_id: int,
    topics: list[str]
):
    """
    CREATE Topic nodes and connect:
    (User)-[:HAS_TOPIC]->(Topic)
    (Message)-[:MENTIONS]->(Topic)
    """
    query = """
    MATCH (u:User {id: $user_id})
    MATCH (m:Message)
    WHERE id(m) = $message_id
    MERGE (t:Topic {name: $topic, user_id: $user_id})
      ON CREATE SET t.created_at = datetime()
    MERGE (u)-[:HAS_TOPIC]->(t)
    MERGE (m)-[:MENTIONS]->(t)
    """

    for topic in topics:
        neo4j_db.run_query(
            query,
            {
                "user_id": user_id,
                "message_id": message_id,
                "topic": topic
            }
        )


def fetch_topic_memory(
    user_id: int,
    topic: str,
    exclude_message_id: int,
    limit: int = 3
):
    """
    Fetch previous messages that mentioned the same topic
    (excluding the current message)
    """
    query = """
    MATCH (u:User {id: $user_id})-[:HAS_TOPIC]->(t:Topic {name: $topic})
    MATCH (m:Message)-[:MENTIONS]->(t)
    WHERE id(m) <> $exclude_message_id
    RETURN
      m.content AS content,
      m.timestamp AS timestamp
    ORDER BY m.timestamp DESC
    LIMIT $limit
    """

    return neo4j_db.run_query(
        query,
        {
            "user_id": user_id,
            "topic": topic,
            "exclude_message_id": exclude_message_id,
            "limit": limit
        }
    )
