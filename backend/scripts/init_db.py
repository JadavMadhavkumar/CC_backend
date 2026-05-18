"""
Database initialization script.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import init_db, drop_db
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


async def main():
    """Initialize database tables."""
    configure_logging()
    logger.info("Initializing database...")

    await init_db()
    logger.info("Database initialized successfully")


if __name__ == "__main__":
    asyncio.run(main())