import asyncio

from loguru import logger
from typing_extensions import Literal

from models import Account, MintSoulData
from loader import config

from .api import CarvAPI
from .exceptions.base import APIError
from .utils import random_delay


class CarvBot(CarvAPI):
    MAX_RETRIES = 3
    RETRY_DELAY_LONG = 300
    RETRY_DELAY_SHORT = 60

    def __init__(self, account: Account):
        super().__init__(account)

    async def _retry_request(self, func, *args, **kwargs):
        for _ in range(self.MAX_RETRIES):
            try:
                return await func(*args, **kwargs)

            except APIError as error:
                logger.error(f"APIError: {error.__str__()} | Retrying...")
                delay = (
                    self.RETRY_DELAY_LONG
                    if error.code == 4300
                    else self.RETRY_DELAY_SHORT
                )
                await asyncio.sleep(delay)

            except Exception as error:
                logger.error(f"Error: {error} | Retrying...")
                await asyncio.sleep(self.RETRY_DELAY_SHORT)

    async def mint_soul(
        self, network: Literal["RONIN", "OP", "ZK", "LINEA"]
    ) -> MintSoulData:
        mint_data = await self._retry_request(
            self.get_mint_soul_data, network if network != "RONIN" else "RONIN"
        )

        if network != "RONIN":
            tx_hash = self.wallet.process_mint_transaction(mint_data, network)
            mint_data.tx_hash = tx_hash

        return mint_data

    async def process_mint(self):
        for network in config.networks:
            try:
                if network != "RONIN":
                    if self.wallet.get_balance(network) == 0:
                        logger.warning(
                            f"Account: {self.wallet.address} | Insufficient balance for mint | Network: {network}"
                        )
                        continue

                if await self.is_available_to_claim(network):
                    mint_data = await self.mint_soul(network)
                    logger.success(
                        f"Account: {self.wallet.address} | Minted soul successfully: {mint_data.permit.amount} | Network: {network}"
                    )
                else:
                    logger.warning(
                        f"Account: {self.wallet.address} | No soul available to mint | Network: {network}"
                    )

            except Exception as error:
                logger.error(f"Failed to mint soul: {error} | Network: {network}")

            await random_delay()

    async def process_claim_rewards(self) -> None:
        rewards_list = await self._retry_request(self.get_rewards_list)

        if not rewards_list.data_rewards:
            logger.info(
                f"Account: {self.wallet.address} | No rewards available to claim"
            )
            return

        for reward in rewards_list.data_rewards:
            try:
                await self._retry_request(self.claim_reward, reward.id)
                logger.success(
                    f"Account: {self.wallet.address} | Claimed reward successfully: {reward.id} | Amount: {reward.soul_count} | Description: {reward.description}"
                )

            except Exception as error:
                logger.error(
                    f"Failed to claim reward: {error} | Reward ID: {reward.id}"
                )

            await random_delay()

    async def start(self) -> None:
        try:
            await self.login()
            await self.process_mint()
            await self.process_claim_rewards()
            logger.success(
                f"Account: {self.wallet.address} | Daily actions completed | Waiting for next cycle..."
            )

        except Exception as error:
            logger.error(
                f"Account: {self.wallet.address} | Failed to start bot: {error}"
            )
