import asyncio
import noble_tls
import pyuseragents
import requests

from typing_extensions import Literal
from loguru import logger

from .wallet import Wallet
from models import *
from .exceptions.base import APIError


CHAINS_IDS = {
    "RONIN": 2020,
    "OP": 204,
    "ZK": 324,
    "LINEA": 59144,
}


class CarvAPI(noble_tls.Session):
    API_URL = "https://interface.carv.io"

    def __init__(self, account: Account):
        super().__init__()

        self.account = account
        self.wallet = Wallet(
            pk_or_mnemonic=account.pk_or_mnemonic, session=self.build_web3_session()
        )
        self.setup_session()

    def build_web3_session(self) -> requests.Session:
        web3_session = requests.Session()
        web3_session.proxies = {"http": self.account.proxy, "https": self.account.proxy}

        return web3_session

    def setup_session(self):
        self.client_identifier = "chrome_120"
        self.random_tls_extension_order = True
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,ru;q=0.8",
            "authorization": "",
            "origin": "https://protocol.carv.io",
            "referer": "https://protocol.carv.io/",
            "user-agent": pyuseragents.random(),
            "x-app-id": "carv",
        }

        self.proxies = {"http": self.account.proxy, "https": self.account.proxy}

    async def send_request(
        self,
        request_type: Literal["POST", "GET"] = "POST",
        method: str = None,
        url: str = None,
        json_data: dict = None,
        params: dict = None,
        data: str = None,
    ) -> dict:

        def _verify_response(_data: dict) -> dict:
            if "code" in _data:
                if _data["code"] != 0:
                    raise APIError(_data)

            return _data

        try:
            if request_type == "POST":
                if url:
                    response = await self.post(
                        url, json=json_data, params=params, data=data
                    )
                else:
                    response = await self.post(
                        f"{self.API_URL}{method}",
                        json=json_data,
                        params=params,
                        data=data,
                    )

            else:
                if url:
                    response = await self.get(url, params=params, data=data)
                else:
                    response = await self.get(
                        f"{self.API_URL}{method}", params=params, data=data
                    )

        except Exception as error:
            raise APIError({"code": -1, "msg": str(error)})

        return _verify_response(response.json())

    async def get_signature_text(self) -> str:
        response = await self.send_request(
            method="/protocol/wallet/get_signature_text", request_type="GET"
        )
        return response["data"]["text"]

    async def login(self) -> None:
        signature_text = await self.get_signature_text()
        signature = self.wallet.get_signature(signature_text)

        json_data = {
            "wallet_addr": self.wallet.address,
            "text": signature_text,
            "signature": signature,
        }

        response = await self.send_request(
            method="/protocol/login", json_data=json_data
        )
        self.headers["authorization"] = f"bearer {response['data']['token']}"

        logger.success(f"Account: {self.wallet.address} | Logged in successfully")

    async def get_mint_soul_data(
        self, network: Literal["RONIN", "OP", "ZK", "LINEA"]
    ) -> MintSoulData:
        json_data = {
            "chain_id": CHAINS_IDS[network],
        }

        response = await self.send_request(
            method="/airdrop/mint/carv_soul", json_data=json_data
        )
        return MintSoulData(**response["data"])

    async def get_balance(self) -> int:
        response = await self.send_request(
            method="/airdrop/soul/balance", request_type="GET"
        )
        return response["data"]["balance"]

    async def is_available_to_claim(
        self, network: Literal["RONIN", "OP", "ZK", "LINEA"]
    ) -> bool:
        params = {
            "chain_id": CHAINS_IDS[network],
        }

        response = await self.send_request(
            method="/airdrop/check_carv_status", params=params, request_type="GET"
        )
        return False if response["data"]["status"] == "finished" else True

    async def get_rewards_list(self) -> RewardsList:
        response = await self.send_request(
            method="/airdrop/data_rewards/list", request_type="GET"
        )
        return RewardsList(**response["data"])

    async def claim_reward(self, reward_id: int) -> None:
        json_data = {
            "id": reward_id,
        }

        await self.send_request(
            method="/airdrop/data_rewards/claim", json_data=json_data
        )


#     async def start(self):
#         await self.login()
#         await self.process_mint()
#
#
#
# if __name__ == "__main__":
#     bot = CarvBot("setup vessel service meadow say neither certain spatial demand sea elder tennis")
#     asyncio.run(bot.start())
