import time
import logging
from groq import Groq
import config

logger = logging.getLogger("repoverse")

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=config.get_groq_api_key())
    return _client


def call_groq(prompt: str, max_retries: int = 2, retry_delay_seconds: int = 2) -> str:
    client = _get_client()
    last_error = None

    for attempt in range(1, max_retries + 2):
        try:
            response = client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            if not response.choices:
                raise ValueError("Groq returned no choices in the response.")

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Groq returned an empty answer.")

            return content

        except Exception as e:
            last_error = e
            logger.warning(f"Groq call failed on attempt {attempt}: {e}")
            if attempt <= max_retries:
                time.sleep(retry_delay_seconds)

    raise RuntimeError(f"Groq call failed after {max_retries + 1} attempts. Last error: {last_error}")
