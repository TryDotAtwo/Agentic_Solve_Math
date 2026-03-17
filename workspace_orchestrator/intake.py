from __future__ import annotations

import re
from pathlib import Path

from .models import IntakeBrief


URL_RE = re.compile(r"https?://[^\s)>\"']+")
PRIORITY_PREFIXES = ("- ", "* ")


def _classify_url(url: str, brief: IntakeBrief) -> None:
    lowered = url.lower()
    if "kaggle.com/competitions/" in lowered and "discussion" in lowered:
        brief.discussion_links.append(url)
    elif "kaggle.com/code/" in lowered:
        brief.notebook_links.append(url)
    elif "kaggle.com/competitions/" in lowered:
        brief.competition_links.append(url)
    elif "github.com/" in lowered or "gitlab.com/" in lowered:
        brief.repo_links.append(url)
    elif any(token in lowered for token in ("arxiv.org", "doi.org", "semanticscholar.org", "openreview.net")):
        brief.paper_links.append(url)
    else:
        brief.other_links.append(url)


def parse_intake_file(path: Path) -> IntakeBrief:
    text = path.read_text(encoding="utf-8")
    brief = IntakeBrief(source_file=path)

    for url in URL_RE.findall(text):
        _classify_url(url.rstrip(".,;"), brief)

    current_section = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            current_section = line.lstrip("#").strip().lower()
            continue
        if not line:
            continue
        if line.startswith(PRIORITY_PREFIXES) and "priorit" in current_section:
            brief.priorities.append(line[2:].strip())
            continue
        if current_section in {"optional notes from user", "notes", "optional notes"} and line.startswith(PRIORITY_PREFIXES):
            brief.notes.append(line[2:].strip())

    return brief


def find_latest_intake_file(intake_dir: Path) -> Path:
    candidates = [
        path
        for path in intake_dir.glob("*.md")
        if path.name not in {"README.md", "_TEMPLATE_KAGGLE_INPUT.md"}
    ]
    if not candidates:
        raise FileNotFoundError(f"No intake markdown files found in {intake_dir}")
    return max(candidates, key=lambda item: item.stat().st_mtime)
