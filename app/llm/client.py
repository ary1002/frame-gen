import anthropic
from app.config import get_settings

_client: anthropic.AsyncAnthropic | None = None


def get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=get_settings().ANTHROPIC_API_KEY)
    return _client


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
