#!/usr/bin/env python3
"""Update GitHub repository description and topics via the REST API.

This makes the repository discoverable via GitHub search and topic pages,
which is a key part of AEO/GEO for code repositories.

Usage:
    export GITHUB_TOKEN=ghp_xxx
    python scripts/update_github_metadata.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not TOKEN:
    print("ERROR: GITHUB_TOKEN environment variable is not set.", file=sys.stderr)
    sys.exit(1)

REPO = "modarresi1913/Aletheia-ai"

DESCRIPTION = (
    "An experimental Reflective Intelligence architecture for epistemic clarity, "
    "self-understanding, and autonomous human choice. Not a chatbot. Not a guru. "
    "An instrument. Enforced seven-label epistemic system + runtime safety constitution."
)

TOPICS = [
    "reflective-intelligence",
    "epistemology",
    "ai-alignment",
    "ai-safety",
    "philosophy",
    "wisdom-graph",
    "socratic-ai",
    "self-understanding",
    "contemplative-ai",
    "introspective-ai",
    "ai-ethics",
    "open-source-ai",
    "epistemic-honesty",
    "anti-sycophancy",
    "llm-architecture",
    "fastapi",
    "pydantic",
    "ollama",
    "python",
    "research",
]


def update_description() -> None:
    url = f"https://api.github.com/repos/{REPO}"
    data = json.dumps({"description": DESCRIPTION, "homepage": ""}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="PATCH",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            print(f"[ok] description set: {body.get('description', '')[:80]}...")
    except urllib.error.HTTPError as e:
        print(f"[err] description update failed: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)


def update_topics() -> None:
    url = f"https://api.github.com/repos/{REPO}/topics"
    data = json.dumps({"names": TOPICS}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="PUT",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github.mercy-preview+json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            print(f"[ok] topics set: {body.get('names', [])}")
    except urllib.error.HTTPError as e:
        print(f"[err] topics update failed: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)


if __name__ == "__main__":
    update_description()
    update_topics()
