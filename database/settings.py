# Standard library imports
import asyncio
from os import path


# Third party imports
from sqlalchemy.ext.asyncio import create_async_engine

# Local application imports
from configs.constants import POSTGRESQL_USERNAME, POSTGRESQL_PASSWORD


engine = create_async_engine(f"postgresql+asyncpg://{POSTGRESQL_USERNAME}:{POSTGRESQL_PASSWORD}@localhost/pprogramistbot")


