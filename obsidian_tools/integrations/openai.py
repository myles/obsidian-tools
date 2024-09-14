from dataclasses import asdict, dataclass
from typing import List, Union

from requests.auth import AuthBase

from obsidian_tools.utils.http_client import HttpClient, RequestReturn


@dataclass
class ChatMessage:

    def to_dict(self):
        return asdict(self)


@dataclass
class ChatMessageSystem(ChatMessage):

    content: Union[str, List[str]]
    name: Union[str, None] = None

    role = "system"


@dataclass
class ChatMessageUser(ChatMessage):

    content: Union[str, List[str]]
    name: Union[str, None] = None

    role = "user"


class OpenAIAuth(AuthBase):
    def __init__(
        self,
        api_key: str,
        organization_id: str,
        project_id: Union[str, None] = None,
    ):
        self.api_key = api_key
        self.organization_id = organization_id
        self.project_id = project_id

    def __call__(self, request):
        request.headers["Authorization"] = f"Bearer {self.api_key}"

        request.headers["OpenAI-Organization"] = self.organization_id

        if self.project_id is not None:
            request.headers["OpenAI-Project"] = self.project_id

        return request


class OpenAIClient(HttpClient):
    """
    A client for the OpenAI API.
    """

    def __init__(
        self,
        api_key: str,
        organization_id: str,
        project_id: Union[str, None] = None,
        **kwargs,
    ):
        auth = OpenAIAuth(
            api_key=api_key,
            organization_id=organization_id,
            project_id=project_id,
        )
        super().__init__(auth=auth, **kwargs)

        self.base_url = "https://api.openai.com/v1"

    def chat_completion(
        self,
        messages: List[ChatMessage],
        model: str = "gpt-3.5-turbo",
        **kwargs,
    ) -> RequestReturn:
        """
        Get a completion from the chat endpoint.

        - Docs: <https://platform.openai.com/docs/api-reference/chat/create>
        """
        url = f"{self.base_url}/chat/completions"

        data = {
            "model": model,
            "messages": [message.to_dict() for message in messages],
        }

        request, response = self.post(url, json=data, **kwargs)
        response.raise_for_status()

        return request, response
