import logging

from sqlalchemy import Engine
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


# Retry logic to check if the DB is ready
@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init_db(db_engine: Engine) -> None:
    try:
        with Session(db_engine) as session:
            # Try to create a session to check if the DB is awake
            session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


# Main function that initializes the service
def main() -> None:
    logger.info("Initializing service")

    # Initialize the database first
    init_db(engine)

    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
