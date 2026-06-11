from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.api.routes import router
from app.db import async_engine, AsyncSessionLocal
from app.llm.prompts import PROMPT_SEEDS
from app.models import Base, PromptTemplate


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables (dev convenience; use alembic for prod migrations)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed PromptTemplate rows
    async with AsyncSessionLocal() as db:
        for seed in PROMPT_SEEDS:
            stmt = (
                pg_insert(PromptTemplate)
                .values(
                    id=seed["id"],
                    kind=seed["kind"],
                    system_prompt=seed["system_prompt"],
                    version=seed["version"],
                )
                .on_conflict_do_nothing(index_elements=["id"])
            )
            await db.execute(stmt)
        await db.commit()

    yield

    # Shutdown: dispose engine
    await async_engine.dispose()


app = FastAPI(title="Pipeline A", version="0.1.0", lifespan=lifespan)
app.include_router(router)
