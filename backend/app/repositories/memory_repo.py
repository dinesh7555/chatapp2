# app/repositories/memory_repo.py

from app.neo4j_db import neo4j_db


def store_embedding(
    message_id: int,
    embedding: list[float]
):
    """
    Store embedding on Message node
    """
    query = """
    MATCH (m:Message)
    WHERE id(m) = $message_id
    SET m.embedding = $embedding
    """

    neo4j_db.run_query(
        query,
        {
            "message_id": message_id,
            "embedding": embedding
        }
    )


def fetch_semantic_memory(
    user_id: int,
    embedding: list[float],
    exclude_message_id: int,
    k: int = 5
):
    """
    Vector similarity search using Neo4j vector index
    """
    query = """
    CALL db.index.vector.queryNodes(
      'message_embedding_index',
      $k,
      $embedding
    )
    YIELD node, score
    WHERE 
      score >= 0.6 AND
      node.role = 'user'
      AND id(node) <> $exclude_message_id
      AND EXISTS {
        MATCH (u:User {id: $user_id})
          -[:HAS_CONVERSATION]->()
          -[:HAS_MESSAGE]->(node)
      }
    RETURN
      node.content AS content,
      node.timestamp AS timestamp,
      score
    ORDER BY score DESC
    """

    return neo4j_db.run_query(
        query,
        {
            "user_id": user_id,
            "embedding": embedding,
            "exclude_message_id": exclude_message_id,
            "k": k
        }
    )
