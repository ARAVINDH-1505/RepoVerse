import subprocess
import hashlib
from pathlib import Path
import config


def clone_github_repo(repo_url: str) -> Path:
    repo_hash = hashlib.md5(repo_url.encode()).hexdigest()[:10]
    dest = config.PROJECT_ROOT / "cloned_repos" / repo_hash

    if dest.exists():
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(dest)],
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        raise RuntimeError(f"git clone failed: {result.stderr.strip()}")

    return dest
