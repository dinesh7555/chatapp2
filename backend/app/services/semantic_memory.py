# app/services/semantic_memory.py

from datetime import datetime, timezone
from neo4j.time import DateTime as Neo4jDateTime

MAX_TOPICS = 3
MAX_MESSAGES_PER_TOPIC = 2
MAX_TOTAL_MESSAGES = 5

def extract_and_clean_topics(topics: list[str]) -> list[str]:
    BAD_WORDS = {
        "explain", "simple", "terms", "here",
        "topics", "clear", "include", "following"
    }

    clean = []
    for t in topics:
        t = t.strip().title()
        if len(t) < 3 or len(t) > 40:
            continue
        if any(w in t.lower() for w in BAD_WORDS):
            continue
        clean.append(t)

    return list(set(clean))


def recency_decay(timestamp) -> float:
    if isinstance(timestamp, Neo4jDateTime):
        timestamp = timestamp.to_native()

    age_days = (datetime.now(timezone.utc) - timestamp).days
    if age_days <= 3:
        return 1.0
    if age_days <= 7:
        return 0.7
    if age_days <= 30:
        return 0.4
    return 0.0


def build_knowledge_context(topic_memories: dict, semantic_texts: list[str]) -> str:
    blocks = []

    # for topic, memories in topic_memories.items():
    #     if not memories:
    #         continue

    #     blocks.append(f"Related discussion about {topic}:")
    #     for m in memories:
    #         blocks.append(f"- {m['content']}")

    if semantic_texts:
        blocks.append("\nRelated previous messages:")
        for text in semantic_texts[:3]:
            blocks.append(f"- {text}")

    return "\n".join(blocks)


def should_use_memory(topic_memories: dict, semantic_texts: list[str]) -> bool:
    return any(topic_memories.values()) or bool(semantic_texts)
