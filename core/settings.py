import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

ROOT = Path(__file__).resolve().parents[1]

# --- OpenRouter настройки ---
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "openrouter/free"
# OPENROUTER_MODEL = "inclusionai/ling-3.0-flash:free"

def create_openrouter_model() -> ChatOpenAI:
    """Создать LangChain-модель для OpenAI-совместимого OpenRouter API."""
    load_dotenv(ROOT / ".env", override=False)
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

    if not api_key or api_key == "put_your_key_here":
        raise RuntimeError(
            "Добавьте OPENROUTER_API_KEY в файл .env."
        )

    # return ChatOpenAI(
    #     model=OPENROUTER_MODEL,
    #     api_key=api_key,
    #     base_url=OPENROUTER_BASE_URL,
    #     use_responses_api=False,
    #     temperature=0,
    #     timeout=180.0,      # OpenRouter иногда отвечает медленнее
    #     max_retries=2,      # Лучше оставить 2 для сетевых сбоев
    # )
    return ChatOpenAI(
        model=OPENROUTER_MODEL,
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
        use_responses_api=False,
        temperature=0,
        timeout=180.0,
        max_retries=2,
        default_headers={  # добавь это
            "HTTP-Referer": "http://localhost",
            "X-Title": "MUT Transport Bot",
        },
    )