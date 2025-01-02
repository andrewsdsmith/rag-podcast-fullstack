from typing import Literal

from pydantic import (
    PostgresDsn,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_FULL_VERSION: str = "1.0.1"
    API_V1_STR: str = "/api/v1"

    FRONTEND_HOST: str = "http://localhost"  # For local development
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    PROJECT_NAME: str

    # OpenAI Model - Generator
    OPENAI_MODEL: str
    OPENAI_API_KEY: str = ""

    # Jina Model - Embedder
    JINA_EMBEDDER_MODEL: str

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
            You are a research assistant focused on accurately conveying scientific health information from the ZOE Science & Nutrition podcast. Your primary role is to connect users with relevant podcast discussions while maintaining scientific accuracy and proper attribution. You always answer with markdown formatting.

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
            
            Instructions:
            1. Please respond to this query with markdown formatting.
            2. Extract relevant information from provided podcast segments
            3. Format response using specified citation style
            4. Ensure every claim links to its source
            5. Acknowledge information gaps if present
            
            """  # noqa: W293


settings = Settings()  # type: ignore
