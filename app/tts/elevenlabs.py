import asyncio
import base64
import json
import tempfile
import os
from typing import AsyncIterator
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings
from app.contracts import AudioBlob, WordTimestamp
from app import storage

_SEMAPHORE = asyncio.Semaphore(5)

class TTSError(Exception):
    pass

def collapse_to_words(
    characters: list[str],
    start_times: list[float],
    end_times: list[float],
) -> list[WordTimestamp]:
    """Collapse character-level alignment to word-level WordTimestamp list."""
    words = []
    current_word = ""
    word_start = None
    word_end = None

    for i, char in enumerate(characters):
        if char in (" ", "\n", "\t"):
            if current_word:
                words.append(WordTimestamp(word=current_word, start_s=word_start, end_s=word_end))
                current_word = ""
                word_start = None
                word_end = None
        else:
            if word_start is None:
                word_start = start_times[i]
            word_end = end_times[i]
            current_word += char

    if current_word:
        words.append(WordTimestamp(word=current_word, start_s=word_start, end_s=word_end))

    return words

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True,
)
async def _call_elevenlabs(voice_id: str, text: str, api_key: str) -> dict:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            url,
            headers={"xi-api-key": api_key, "Content-Type": "application/json"},
            json={"text": text, "model_id": "eleven_multilingual_v2"},
        )
        resp.raise_for_status()
        return resp.json()

async def _measure_duration(audio_bytes: bytes) -> float:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "json", tmp_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        data = json.loads(stdout)
        return float(data["format"]["duration"])
    finally:
        os.unlink(tmp_path)

async def synthesize_slide(
    slide_index: int,
    text: str,
    script_hash: str,
    voice_id: str,
    job_id: str,
) -> tuple[AudioBlob, list[WordTimestamp]]:
    s = get_settings()
    async with _SEMAPHORE:
        try:
            result = await _call_elevenlabs(voice_id, text, s.ELEVENLABS_API_KEY)
        except httpx.HTTPError as e:
            raise TTSError(f"ElevenLabs API error: {e}") from e

    audio_bytes = base64.b64decode(result["audio_base64"])
    alignment = result.get("alignment", {})

    key = f"{job_id}/audio/{slide_index}.mp3"
    storage.put_bytes(key, audio_bytes, "audio/mpeg")
    audio_url = storage.get_presigned_url(key)

    actual_duration_s = await _measure_duration(audio_bytes)

    word_timestamps = collapse_to_words(
        alignment.get("characters", []),
        alignment.get("character_start_times_seconds", []),
        alignment.get("character_end_times_seconds", []),
    )

    blob = AudioBlob(
        slide_index=slide_index,
        url=audio_url,
        actual_duration_s=actual_duration_s,
        voice_id=voice_id,
        script_hash=script_hash,
    )
    return blob, word_timestamps
