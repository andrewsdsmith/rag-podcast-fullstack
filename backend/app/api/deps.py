from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.db import engine
from app.services.pipeline.pipeline_builder import PipelineBuilder


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_pipeline_builder() -> PipelineBuilder:
    return PipelineBuilder()


PipelineBuilderDep = Annotated[PipelineBuilder, Depends(get_pipeline_builder)]
