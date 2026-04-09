from google import genai

from app.core.config import settings

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


MODEL = "gemini-2.5-flash"


async def generate(
    prompt: str,
    system_instruction: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    client = get_client()

    config = genai.types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )

    if system_instruction:
        config.system_instruction = system_instruction

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=config,
    )

    return response.text or ""


async def generate_json(
    prompt: str,
    system_instruction: str = "",
    temperature: float = 0.4,
    max_tokens: int = 2048,
) -> str:
    client = get_client()

    config = genai.types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type="application/json",
    )

    if system_instruction:
        config.system_instruction = system_instruction

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=config,
    )

    return response.text or ""
