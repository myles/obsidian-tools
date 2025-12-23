"""
Module for summarising the Bullet Journal logs.
"""

import typing as t
from pathlib import Path

from frontmatter import Post

from obsidian_tools.integrations.openai import (
    ChatMessageSystem,
    ChatMessageUser,
    OpenAIClient,
)


def summarise_daily_logs(
    daily_logs: t.List[t.Tuple[Path, Post]], client: OpenAIClient
):
    """
    Summarise daily logs.
    """
    daily_logs_sorted = sorted(
        daily_logs,
        key=lambda daily_log: daily_log[0].stem,
    )

    messages = [
        ChatMessageSystem(
            content="I would like you to summarise my daily logs."
        ),
        ChatMessageUser(
            content=[post.content for path, post in daily_logs_sorted]
        ),
    ]

    request, response = client.chat_completion(messages)

    return response.json()
