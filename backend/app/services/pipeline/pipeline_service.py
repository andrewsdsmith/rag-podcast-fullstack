import logging

from fastapi import HTTPException, status

from app.api.deps import DbSession, PipelineBuilderDep

logger = logging.getLogger(__name__)


async def generate_pipeline_prompt(
    question: str,
    pipeline_builder: PipelineBuilderDep,
    session: DbSession,
) -> str:
    """Generate and validate the pipeline prompt."""
    try:
        prompt_augmenter = pipeline_builder.build(session=session)
        pipeline_prompt_model = prompt_augmenter.run(
            {"embedder": {"text": question}, "retriever": {"top_k": 15}}
        )
        prompt: str = pipeline_prompt_model["prompt"]["prompt"]
        logger.info(f"Generated prompt: {prompt[:200]}...")
        return prompt
    except Exception:
        logger.exception("Failed to generate pipeline prompt")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process question",
        )
