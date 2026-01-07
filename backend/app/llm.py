import requests
from app.config import OPENROUTER_API_KEY

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "meta-llama/llama-3-8b-instruct"


def call_llm(messages: list[dict], system_prompt: str ):
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            *messages
        ]
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    raw_text = data["choices"][0]["message"]["content"]
    return raw_text.replace("<s>", "").replace("</s>", "").strip()


def call_llm_title(user_messages: list[str]) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a conversation title generator. "
                "Summarize the topic in 3 to 6 words. "
                "Return ONLY the title. "
                "Do NOT explain. "
                "Do NOT use full sentences."
            )
        }
    ] + [
        {"role": "user", "content": msg}
        for msg in user_messages
    ]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 20,        
        "temperature": 0.2       
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    title = data["choices"][0]["message"]["content"]

    # sanitize
    title = title.strip().split("\n")[0]
    title = title.replace('"', "").replace("'", "")
    title = " ".join(title.split()[:6])

    return title

def extract_topics(text: str) -> list[str]:
    messages = [
        {
            "role": "system",
            "content": (
                "Extract 1 to 4 high-level topics from the message.\n"
                "Rules:\n"
                "- Return ONLY comma-separated topic names\n"
                "- NO sentences\n"
                "- NO numbering\n"
                "- NO explanations\n"
                "- NO prefixes like 'Here are'\n"
                "- Topics must be nouns or noun phrases\n"
                "Example output:\n"
                "Artificial Intelligence, Machine Learning"

            )
        },
        {"role": "user", "content": text}
    ]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 30,
        "temperature": 0.1
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=15
    )

    response.raise_for_status()
    raw = response.json()["choices"][0]["message"]["content"]

    topics = [
        t.strip().title()
        for t in raw.split(",")
        if t.strip()
    ]

    return topics[:4]
 
# Generate embedding using OpenRouter API
def generate_embedding(text: str) -> list[float]:
    payload = {
        "model": "text-embedding-3-small",
        "input": text
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers=headers,
        json=payload,
        timeout=20
    )

    response.raise_for_status()
    return response.json()["data"][0]["embedding"]
