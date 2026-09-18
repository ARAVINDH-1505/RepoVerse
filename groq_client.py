import time
import logging
import threading
from collections import deque
from groq import Groq
import config

logger = logging.getLogger("repoverse")

_client = None
_token_log = deque()  # list of (timestamp, tokens_used) within the last 60 seconds
_lock = threading.Lock()

TPM_LIMIT = 8000
SAFETY_MARGIN = 0.85  # stay under 85% of the real limit, to leave headroom


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=config.get_groq_api_key())
    return _client


def _wait_for_token_budget(estimated_tokens: int) -> None:
    with _lock:
        now = time.time()
        while _token_log and now - _token_log[0][0] > 60:
            _token_log.popleft()

        used = sum(tokens for _, tokens in _token_log)
        budget = TPM_LIMIT * SAFETY_MARGIN

        if used + estimated_tokens > budget:
            oldest_timestamp = _token_log[0][0] if _token_log else now
            wait_seconds = max(0.0, 60 - (now - oldest_timestamp)) + 1
            logger.info(f"Pausing {wait_seconds:.1f}s to stay under Groq's tokens-per-minute limit")
            time.sleep(wait_seconds)


def _record_tokens(tokens: int) -> None:
    with _lock:
        _token_log.append((time.time(), tokens))


def call_groq(prompt: str, max_retries: int = 2, retry_delay_seconds: int = 2) -> str:
    client = _get_client()
    last_error = None

    # Rough estimate before we know the real usage: ~4 characters per token,
    # plus a buffer for the model's response.
    estimated_tokens = (len(prompt) // 4) + 500

    for attempt in range(1, max_retries + 2):
        try:
            _wait_for_token_budget(estimated_tokens)

            response = client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )

            actual_tokens = estimated_tokens
            if getattr(response, "usage", None) and getattr(response.usage, "total_tokens", None):
                actual_tokens = response.usage.total_tokens
            _record_tokens(actual_tokens)

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
