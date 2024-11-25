from contextlib import asynccontextmanager
from typing import Any

import openai
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.routing import APIRoute
from sqlmodel import Session, select
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.db import engine
from app.models.prompt import Prompt


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> Any:
    # Load the OpenAI API key from the environment
    openai.api_key = settings.OPENAI_API_KEY

    # Load the environment variables from the .env file
    load_dotenv()

    # Check the version in the prompt table and update if necessary
    with Session(engine) as session:
        prompt = session.exec(
            select(Prompt).where(Prompt.api_version == settings.API_FULL_VERSION)
        ).first()
        if not prompt:
            # Create a new prompt
            prompt = Prompt(
                api_version=settings.API_FULL_VERSION, text=settings.PROMPT_TEMPLATE
            )
            session.add(prompt)
            session.commit()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
