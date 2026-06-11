"""Stage 6: invoke Node render.mjs as a subprocess and stream progress to DB."""
import asyncio
import json
import os
import tempfile
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job

# app/pipeline/render.py → ../../remotion/render.mjs
_RENDER_MJS = Path(__file__).parent.parent.parent / "remotion" / "render.mjs"


async def run_render_job(job_id: str, schema_key: str, db: AsyncSession) -> str:
    """
    1. Download RemotionSchema JSON from MinIO to a temp file
    2. Run: node render.mjs <schema_path> <output_mp4_path>
    3. Stream JSON progress lines → update job.render_progress in DB
    4. Upload output MP4 to MinIO and return presigned URL
    """
    from app import storage  # deferred to avoid boto3 at import time
    schema_dict = storage.get_json(schema_key)

    with tempfile.TemporaryDirectory() as tmpdir:
        schema_path = os.path.join(tmpdir, "schema.json")
        output_path = os.path.join(tmpdir, "output.mp4")

        with open(schema_path, "w") as f:
            json.dump(schema_dict, f)

        proc = await asyncio.create_subprocess_exec(
            "node", str(_RENDER_MJS), schema_path, output_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(_RENDER_MJS.parent),
        )

        job = await db.get(Job, uuid.UUID(job_id))

        async for raw_line in proc.stdout:
            line = raw_line.decode().strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            if "progress" in msg:
                job.render_progress = msg["progress"] / 100.0
                await db.commit()
            elif msg.get("done"):
                break

        await proc.wait()

        if proc.returncode != 0:
            stderr = await proc.stderr.read()
            raise RuntimeError(
                f"render.mjs exited {proc.returncode}: {stderr.decode()}"
            )

        with open(output_path, "rb") as f:
            mp4_bytes = f.read()

    from app import storage
    video_key = f"{job_id}/output.mp4"
    storage.put_bytes(video_key, mp4_bytes, "video/mp4")
    return storage.get_presigned_url(video_key, expires=86400)
