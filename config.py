import os
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

PROJECT_ROOT = Path(__file__).resolve().parent


def _load_dotenv_key(key_name: str) -> str | None:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return None

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = [part.strip() for part in line.split("=", 1)]
        if key == key_name and value:
            return value.strip("\"'")

    return None


def get_groq_api_key() -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return api_key

    api_key = _load_dotenv_key("GROQ_API_KEY")
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
        return api_key

    raise RuntimeError(
        "GROQ_API_KEY is missing. Set it as an environment variable, "
        "or add GROQ_API_KEY=your_key to a .env file in the project root."
    )


# Groq retired llama-3.1-8b-instant and llama-3.3-70b-versatile.
# openai/gpt-oss-20b is the current fast, free-tier-friendly default.
# Override by setting GROQ_MODEL as an environment variable or in .env.
GROQ_MODEL = os.getenv("GROQ_MODEL") or _load_dotenv_key("GROQ_MODEL") or "openai/gpt-oss-20b"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

MAX_AGENT_ITERATIONS = 3

CHROMA_DATA_PATH = str(PROJECT_ROOT / "chroma_data")

DEFAULT_FILE_TYPES = [
    ".py", ".md", ".json",
    ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rs", ".cpp", ".c", ".h",
    ".html", ".css", ".yaml", ".yml",
]

# Bug Finder's syntax check uses Python's own ast.parse, which only understands
# Python. It intentionally only scans .py files for now, regardless of this
# list - scanning other languages here would produce false syntax-error claims.

# Only folder_path values inside this directory (or its subfolders) are
# accepted by the API. Defaults to the user's home directory; override with
# the REPOVERSE_ALLOWED_ROOT environment variable for a narrower scope.
ALLOWED_PROJECT_ROOT = (
    os.getenv("REPOVERSE_ALLOWED_ROOT")
    or _load_dotenv_key("REPOVERSE_ALLOWED_ROOT")
    or str(Path.home())
)

# Groq's free tier caps each request around 8000 tokens (~4 characters per token).
# check_accuracy() sends the code context twice in one prompt, so we keep this
# conservative to leave room for that, plus the summary text and prompt wording.
MAX_TOTAL_CONTEXT_CHARS = 4000

# Shared per-file truncation limit, used anywhere a single file's raw content
# is sent to Groq (Summarizer's per-file pass, Bug Finder's per-file scan).
# One file alone stays well under the token limit even at this size.
MAX_CHARS_PER_FILE = 3000

# Small pause between back-to-back Groq calls in loops that call it once per
# file (like the Summarizer), to avoid triggering rate limits reactively.
PER_FILE_CALL_DELAY_SECONDS = 1.5
