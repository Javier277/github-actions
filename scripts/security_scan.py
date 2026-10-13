"""Simulated security scan: looks for exposed API keys in the repository.

Used by .github/workflows/20.desafio_final.yaml. Exits with code 1 if any
suspicious key is found, which makes the workflow step fail.
"""

import re
import sys
from pathlib import Path

SUSPICIOUS_PATTERNS = {
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "OpenAI-style secret key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "Hardcoded api_key": re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"),
}

SCANNED_EXTENSIONS = {".py", ".json", ".yaml", ".yml", ".txt", ".md", ".env"}
IGNORED_DIRECTORIES = {".git", "node_modules", ".venv"}


def should_scan(path: Path) -> bool:
    if any(part in IGNORED_DIRECTORIES for part in path.parts):
        return False
    return path.is_file() and path.suffix in SCANNED_EXTENSIONS


def find_leaks(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [
        f"{path}: possible {name}"
        for name, pattern in SUSPICIOUS_PATTERNS.items()
        if pattern.search(text)
    ]


def main() -> int:
    this_script = Path(__file__).resolve()
    files = [p for p in Path(".").rglob("*") if should_scan(p) and p.resolve() != this_script]
    leaks = [leak for file in files for leak in find_leaks(file)]

    print(f"Scanned {len(files)} files")
    if leaks:
        print("Exposed keys found:")
        for leak in leaks:
            print(f"  - {leak}")
        return 1

    print("No exposed API keys found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
