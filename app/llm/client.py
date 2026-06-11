import anthropic
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings

_client: anthropic.AsyncAnthropic | None = None


def reset_client() -> None:
    """Call this in Celery worker init to avoid inheriting parent's connection pool."""
    global _client
    _client = None


def get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(
            api_key=get_settings().ANTHROPIC_API_KEY,
            timeout=httpx.Timeout(connect=30.0, read=600.0, write=30.0, pool=30.0),
            max_retries=0,  # we handle retries via tenacity below
        )
    return _client


@retry(
    retry=retry_if_exception_type((anthropic.APITimeoutError, anthropic.APIConnectionError)),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(4),
    reraise=True,
)
async def call_with_tool(
    system: str,
    user: str,
    tool_name: str,
    tool_description: str,
    input_schema: dict,
) -> dict:
    """Call Claude with forced tool use; returns the tool input dict."""
    client = get_client()
    response = await client.messages.create(
        model=get_settings().CLAUDE_MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
        tools=[
            {
                "name": tool_name,
                "description": tool_description,
                "input_schema": input_schema,
            }
        ],
        tool_choice={"type": "tool", "name": tool_name},
    )
    for block in response.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input
    raise ValueError(f"Tool {tool_name} not called in response")
