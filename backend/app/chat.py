from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.neo4j_db import neo4j_db
import uuid
from app.schemas import ChatMessageRequest
from app.llm import call_llm, call_llm_title, extract_topics ,generate_embedding
from datetime import datetime, timezone

router = APIRouter(prefix="/chat", tags=["Chat"])

def fetch_topic_memory(user_id: int, topic: str,current_message_id:int, limit: int = 5):
        query = """
            MATCH (u:User {id: $user_id})-[:HAS_TOPIC]->(t:Topic {name: $topic})
            MATCH (m:Message)-[:MENTIONS]->(t)
            WHERE id(m) <> $current_message_id
            RETURN m.content AS content, m.timestamp AS timestamp
            ORDER BY m.timestamp DESC
            LIMIT $limit
        """
        return neo4j_db.run_query(
            query,
            {
            "user_id": user_id,
            "topic": topic,
            "current_message_id": current_message_id,
            "limit": limit
            }
        )

MAX_TOPICS = 3
MAX_MESSAGES_PER_TOPIC = 2
MAX_TOTAL_MESSAGES = 5
    
def deduplicate_memories(topic_memories: dict) -> dict:
    seen = set()
    clean = {}

    for topic, memories in topic_memories.items():
        filtered = []
        for m in memories:
            key = m["content"].strip()
            if key in seen:
                continue
            seen.add(key)
            filtered.append(m)
        clean[topic] = filtered
    return clean

def build_implicit_memory_context(topic_memories, semantic_texts):
        blocks = []

        for topic, memories in topic_memories.items():
            if not memories:
                continue
            blocks.append(f"Related previous discussion about {topic}:")
            for m in memories:
                blocks.append(f"- {m['content']}")

        if semantic_texts:
            blocks.append("\nRelated previous messages:")
            for text in semantic_texts[:3]:
                blocks.append(f"- {text}")

        return "\n".join(blocks)

def build_system_prompt(knowledge_context: str | None = None) -> str:
    base_prompt = (
            "You are a helpful AI assistant.\n"
            "Answer the user's question clearly and accurately."
             "Do NOT assume prior conversation unless explicitly shown.\n"
            "Do NOT say phrases like 'previous discussions' or 'earlier conversations'."
    )

    if not knowledge_context:
        return base_prompt

    return (
        base_prompt
        + "\n\n"
        + "The following is OPTIONAL reference information. "
        + "It is NOT part of the current conversation.\n"
        + "Use it only if directly relevant.\n\n"
        + knowledge_context
    )

def fetch_semantic_memory(user_id: int, embedding: list[float], k: int = 5):
    query = """
    CALL db.index.vector.queryNodes(
      'message_embedding_index',
      $k,
      $embedding
    )
    YIELD node, score
    WHERE node.role = 'user'
    AND node.timestamp >= datetime() - duration('P30D')
    AND EXISTS {
        MATCH (u:User {id: $user_id})-[:HAS_CONVERSATION]->()-[:HAS_MESSAGE]->(node)
    }
    RETURN node.content AS content,node.timestamp AS timestamp, score
    ORDER BY score DESC
    """
    return neo4j_db.run_query(
        query,
        {
            "user_id": user_id,
            "embedding": embedding,
            "k": k
        }
    )

from datetime import datetime, timezone
from neo4j.time import DateTime as Neo4jDateTime

def recency_decay(timestamp) -> float:
    now = datetime.now(timezone.utc)
    # 🔹 Convert Neo4j DateTime → Python datetime
    if isinstance(timestamp, Neo4jDateTime):
        timestamp = timestamp.to_native()

    age_days = (now - timestamp).days

    if age_days <= 3:
        return 1.0
    if age_days <= 7:
        return 0.7
    if age_days <= 30:
        return 0.4
    return 0.0


#check if any memory is relevant
def is_memory_relevant(topic_memories: dict) -> bool:
    for memories in topic_memories.values():
        if memories:   # at least one past message exists
            return True
    return False
@router.post("/start")
def start_chat(current_user=Depends(get_current_user)):
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
    # Verify conversation belongs to user
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

    # Store user message
    user_message_query = """
    MATCH (c:Conversation {id: $conversation_id})
    CREATE (m:Message {
        role: "user",
        content: $content,
        timestamp: datetime()
    })
    CREATE (c)-[:HAS_MESSAGE]->(m)
    RETURN id(m) AS message_id
    """

    user_message_result =neo4j_db.run_query(
        user_message_query,
        {
            "conversation_id": data.conversation_id,
            "content": data.message
        }
    )
    message_id = user_message_result[0]["message_id"]
   
    # 🔹 STEP 2.2 — generate and store embedding (WRITE)

    try:
        query_embedding = generate_embedding(data.message)

        neo4j_db.run_query(
            """
            MATCH (m:Message)
            WHERE id(m) = $message_id
            SET m.embedding = $embedding
            """,
            {
                "message_id": message_id,
                "embedding": query_embedding
            }
        )
    except Exception as e:
        # Do NOT fail the request
        print("Embedding generation failed:", e)
     

    #topic extraction
    topics = extract_topics(data.message)
    BAD_WORDS = {
    "explain", "simple", "terms", "here", "are",
    "topics", "clear", "include", "following"
    }

    clean_topics = []

    for t in topics:
        t = t.strip().title()
        # reject very short or long junk
        if len(t) < 3 or len(t) > 40:
            continue
        # reject instruction noise
        if any(word in t.lower() for word in BAD_WORDS):
            continue

        clean_topics.append(t)
        topics = list(set(clean_topics))

    if not topics:
        topics = []
    topics = list(set(t.strip().title() for t in topics))


    # Store topics as properties on the message node
    topic_query = """
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
            topic_query,
            {
            "user_id": current_user.id,
            "topic": topic,
            "message_id": message_id
            }
        )
    
    

    # assemble topic memories (READ ONLY)
    topic_memories = {}

    for topic in topics:
        memories = fetch_topic_memory(
            user_id=current_user.id,
            topic=topic,
            current_message_id=message_id,
            limit=3
        )
        topic_memories[topic] = memories

    

    limited_memories = {}
    total_messages = 0

    for topic in list(topic_memories.keys())[:MAX_TOPICS]:
        msgs = topic_memories[topic][:MAX_MESSAGES_PER_TOPIC]

        if not msgs:
            continue

        if total_messages + len(msgs) > MAX_TOTAL_MESSAGES:
            msgs = msgs[: MAX_TOTAL_MESSAGES - total_messages]

        limited_memories[topic] = msgs
        total_messages += len(msgs)

        if total_messages >= MAX_TOTAL_MESSAGES:
            break
    
    topic_memories = deduplicate_memories(topic_memories)
    semantic_memories = []

    if query_embedding is not None:
        semantic_memories = fetch_semantic_memory(
            user_id=current_user.id,
            embedding=query_embedding,
            k=5
        )

    scored_semantic_memories = []

    for m in semantic_memories:
        decay = recency_decay(m["timestamp"])
        final_score = m["score"] * decay

        if final_score > 0:
            scored_semantic_memories.append({
                "content": m["content"],
                "score": final_score
            })
    scored_semantic_memories.sort(
        key=lambda x: x["score"],
        reverse=True
    )
    semantic_texts = [
        m["content"]
        for m in scored_semantic_memories[:3]
    ]

    knowledge_context = build_implicit_memory_context(
        topic_memories,
        semantic_texts
    )

    print("=== Knowledge Context ===")
    print(knowledge_context)
    print
    #  Fetch recent chat history for context
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
        if h["role"] =="user"
    ]

    use_memory = (
        is_memory_relevant(topic_memories)
        or bool(semantic_texts)
    )

    system_prompt = build_system_prompt(
        knowledge_context if use_memory else None
    )

    print("Semantic memories:", semantic_texts)
    #  assistant response (LLM later)
    print("\n===== SYSTEM PROMPT =====")
    print(system_prompt)
    print("========================\n")

    assistant_reply = call_llm(
        messages=messages,
        system_prompt=system_prompt
    )

    #  Store assistant message
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
    # Fetch current conversation title
    title_query = """
        MATCH (c:Conversation {id: $conversation_id})
        RETURN c.title AS title
    """

    title_result = neo4j_db.run_query(
    title_query,
    {"conversation_id": data.conversation_id}
    )
    current_title = title_result[0]["title"] if title_result else None

    # 🔹 Count user messages
    count_query = """
        MATCH (c:Conversation {id: $conversation_id})-[:HAS_MESSAGE]->(m:Message {role: "user"})
        RETURN count(m) AS user_message_count
    """

    count_result = neo4j_db.run_query(
        count_query,
        {"conversation_id": data.conversation_id}
    )

    user_message_count = count_result[0]["user_message_count"]
    should_generate_title = (
        (current_title is None or current_title == "New Chat")
        and user_message_count > 2
    )
    # 🔹 Generate and update title if needed
    if should_generate_title:
    # 🔹 Fetch minimal context (last few messages)
        context_query = """
            MATCH (c:Conversation {id: $conversation_id})-[:HAS_MESSAGE]->(m:Message {role: "user"})
            RETURN m.content AS content
            ORDER BY m.timestamp ASC
            LIMIT 3
        """

        context = neo4j_db.run_query(
            context_query,
            {"conversation_id": data.conversation_id}
        )
        user_texts = [msg["content"] for msg in context]
        title = call_llm_title(user_texts)
        # --- sanitize AI output ---
        title = title.strip().split("\n")[0]
        title = title.replace('"', "").replace("'", "")
        title = " ".join(title.split()[:6])

        # --- fallback if AI fails ---
        if not title or len(title.strip()) < 3:
        # fallback to first user message
            for msg in context:
                title = " ".join(msg["content"].split()[:6])
                break
        # final safety
        if not title:
            title = "New Chat"


        # Save title to conversation
        update_title_query = """
            MATCH (c:Conversation {id: $conversation_id})
            SET c.title = $title
        """

        neo4j_db.run_query(
            update_title_query,
            {
                "conversation_id": data.conversation_id,
                "title": title
            }
        )
    return {
    "role": "assistant",
    "content": assistant_reply
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
@router.get("/conversations")
def list_conversations(current_user=Depends(get_current_user)):
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

    raw_result = neo4j_db.run_query(
        query,
        {"user_id": current_user.id}
    )

    result = []
    for row in raw_result:
        result.append({
            "conversation_id": row["conversation_id"],
            "title": row["title"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "last_message_time": row["last_message_time"].isoformat() if row["last_message_time"] else None
        })

    return result
