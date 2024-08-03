from importlib.metadata import version

import pytest
import responses

from obsidian_tools.utils import http_client


@responses.activate
@pytest.mark.parametrize("method", list(http_client.HttpMethod))
def test_http_client__request(method: http_client.HttpMethod):
    url = "http://example.com/"

    responses.add(responses.Response(method=str(method.value), url=url))

    client = http_client.HttpClient()
    client.request(method=method, url=url)

    request = responses.calls[0].request  # type: ignore

    expected_user_agent = f"obsidian-tools/{version('obsidian-tools')} (+https://github.com/myles/obsidian-tools/)"
    assert "User-Agent" in request.headers
    assert request.headers["User-Agent"] == expected_user_agent
