import asyncio
import sys
import time

from loguru import logger
from loader import config
from src.bot import CarvBot
from console import load_console


async def run():
    logger.success(
        f"\n\nCarvBot started | Loaded {len(config.accounts)} accounts | Networks: {config.networks}\n\n"
    )
    logger.debug("New cycle started")

    tasks = [
        asyncio.create_task(CarvBot(account).start()) for account in config.accounts
    ]
    await asyncio.gather(*tasks)
    logger.debug("\n\nCycle ended | Next cycle will start at 04:30 AM\n\n")


async def main():
    load_console()
    await run()


async def process_scheduler():
    while True:
        current_time = time.localtime()
        if current_time.tm_hour == 4 and current_time.tm_min >= 30:
            await main()

        time.sleep(30)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
    asyncio.run(process_scheduler())
