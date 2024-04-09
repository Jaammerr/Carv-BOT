import asyncio
import random

from loguru import logger


async def random_delay():
    logger.debug("Random delay..")
    await asyncio.sleep(random.uniform(5, 10))