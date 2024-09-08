"""
Module for summarising the Bullet Journal logs.
"""

from typing import List

from frontmatter import Post

from obsidian_tools.integrations.openai import (
    ChatMessageSystem,
    ChatMessageUser,
    OpenAIClient,
)


def summarise_daily_logs(daily_logs: List[Post], client: OpenAIClient):
    """
    Summarise daily logs.
    """
    messages = [
        ChatMessageSystem(
            content="I would like you to summarise my daily logs."
        ),
        ChatMessageUser(content=[post.content for post in daily_logs]),
    ]

    request, response = client.chat_completion(messages)

    return response.json()
