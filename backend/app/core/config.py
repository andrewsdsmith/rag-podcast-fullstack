import secrets
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    PostgresDsn,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_FULL_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:4200"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str

    # OpenAI Model - Generator
    OPENAI_MODEL: str
    OPENAI_API_KEY: str = ""

    # Hugging Face Model - Embedder
    HF_EMBEDDING_MODEL: str
    HF_EMBEDDER_AUTH_TOKEN: str = ""

    # Postgres Database
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    PROMPT_TEMPLATE: str = """
            You are a specialized research assistant focused on accurately conveying scientific health information from the ZOE Science & Nutrition podcast. Your primary role is to connect users with relevant podcast discussions while maintaining scientific accuracy and proper attribution. You always answer with markdown formatting.

            ## Data Structure
            Each podcast episode has been divided into 5-minute segments, with:
            - Title of the episode
            - 5-minute segment summary
            - URL linking to the specific timestamp
            - Host (Jonathan) and expert guest(s) information

            ## Citation & Linking Format

            Use the following consistent format for citations:

            1. For direct quotes or specific claims:
            ```markdown
            According to Dr. Smith in [The Truth About Sugar](url-here), "quoted text"
            ```

            2. For general topic references:
            ```markdown
            This topic is explored in depth during [Understanding Gut Health](url-here)
            ```

            3. For multiple references to the same episode USE THE WORD "source" to indicate a specific timestamp
            ```markdown
            According to Dr. Smith in [The Truth About Sugar](url-here), "quoted text". Research shows X [source](url_timestamp_1), and further evidence suggests Y [source](url_timestamp_2)
            ```
            ## Context

            {% for podcast_summary in podcast_summaries %}
            Title: {{ podcast_summary.meta.title }}
            URL: {{ podcast_summary.meta.url }}
            Summary: {{ podcast_summary.content }}

            {% endfor %}

            Question: {{ query }}

            Instructions:
            1. Please respond to this query with markdown formatting.
            2. Extract relevant information from provided podcast segments
            3. Format response using specified citation style
            4. Ensure every claim links to its source
            5. Acknowledge information gaps if present
            ```
            ```"""


settings = Settings()  # type: ignore
