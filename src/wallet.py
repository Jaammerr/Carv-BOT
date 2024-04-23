import requests

from typing import Literal

from eth_account.messages import encode_defunct
from web3 import Web3, Account, AsyncWeb3
from web3.middleware import geth_poa_middleware

from models import MintSoulData, LineaContract
from loader import config

Account.enable_unaudited_hdwallet_features()


class Wallet:
    def __init__(self, pk_or_mnemonic: str, session: requests.Session = None):
        self.op_bnb = Web3(Web3.HTTPProvider(config.op_rpc, session=session))
        self.zk_sync = Web3(Web3.HTTPProvider(config.zk_rpc, session=session))
        self.linea = Web3(Web3.HTTPProvider(config.linea_rpc, session=session))
        self.linea.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.op_bnb_wallet = self.op_bnb.eth.account.from_mnemonic(pk_or_mnemonic) if len(pk_or_mnemonic.split()) in (12, 24) else self.op_bnb.eth.account.from_key(pk_or_mnemonic)
        self.zk_sync_wallet = self.zk_sync.eth.account.from_mnemonic(pk_or_mnemonic) if len(pk_or_mnemonic.split()) in (12, 24) else self.zk_sync.eth.account.from_key(pk_or_mnemonic)
        self.linea_wallet = self.linea.eth.account.from_mnemonic(pk_or_mnemonic) if len(pk_or_mnemonic.split()) in (12, 24) else self.linea.eth.account.from_key(pk_or_mnemonic)

        self.linea_contract = self.linea.eth.contract(
            self.linea.to_checksum_address(LineaContract.address), abi=LineaContract.abi
        )

    @property
    def address(self):
        return self.op_bnb_wallet.address

    @property
    def private_key(self):
        return self.op_bnb_wallet._private_key

    def get_balance(self, network: Literal["OP", "ZK", "LINEA"]) -> float:
        balance = (
            self.op_bnb.eth.get_balance(self.address)
            if network == "OP"
            else (
                self.zk_sync.eth.get_balance(self.address)
                if network == "ZK"
                else self.linea.eth.get_balance(self.address)
            )
        )

        human_balance = self.op_bnb.from_wei(balance, "ether")
        return float(human_balance)

    @staticmethod
    def form_hex_data(string: str) -> str:
        if not isinstance(string, str):
            raise ValueError("Input must be a string.")

        if len(string) > 64:
            raise ValueError("String length exceeds 64 characters.")

        return "0" * (64 - len(string)) + string

    def get_signature(self, text: str) -> str:
        encoded_msg = encode_defunct(text=text)
        signed_msg = Web3().eth.account.sign_message(
            encoded_msg, private_key=self.private_key
        )
        return signed_msg.signature.hex()

    def build_transaction_data(self, mint_data: MintSoulData) -> str:
        address_data = self.form_hex_data(mint_data.permit.account[2:])
        amount_data = self.form_hex_data(hex(mint_data.permit.amount)[2:])
        ymd_data = self.form_hex_data(hex(mint_data.permit.ymd)[2:])

        transaction_data = f"0xa2a9539c{address_data}{amount_data}{ymd_data}00000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000041{mint_data.signature[2:]}00000000000000000000000000000000000000000000000000000000000000"
        return transaction_data

    def create_transaction_for_linea(self, mint_data: MintSoulData) -> str:
        transaction = self.linea_contract.functions.mintSoul(
            (
                self.linea.to_checksum_address(mint_data.permit.account),
                mint_data.permit.amount,
                mint_data.permit.ymd,
            ),
            mint_data.signature,
        )

        built_transaction = transaction.build_transaction(
            {
                "value": 0,
                "from": self.linea_wallet.address,
                "nonce": self.linea.eth.get_transaction_count(
                    self.linea_wallet.address
                ),
                "gas": int(
                    transaction.estimate_gas({"from": self.linea_wallet.address}) * 1.2
                ),
            }
        )

        signed = self.linea.eth.account.sign_transaction(
            built_transaction, self.linea_wallet.key
        )
        tx_hash = self.linea.eth.send_raw_transaction(signed.rawTransaction)
        receipt = self.linea.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            return tx_hash.hex()
        else:
            raise Exception(f"Failed to mint soul: {tx_hash.hex()} | Network: LINEA")

    def sign_transaction(self, transaction: dict, network: Literal["OP", "ZK"]) -> str:
        signed = (
            self.op_bnb.eth.account.sign_transaction(
                transaction, self.op_bnb_wallet.key
            )
            if network == "OP"
            else self.zk_sync.eth.account.sign_transaction(
                transaction, self.zk_sync_wallet.key
            )
        )

        tx_hash = (
            self.op_bnb.eth.send_raw_transaction(signed.rawTransaction)
            if network == "OP"
            else self.zk_sync.eth.send_raw_transaction(signed.rawTransaction)
        )

        receipt = (
            self.op_bnb.eth.wait_for_transaction_receipt(tx_hash)
            if network == "OP"
            else self.zk_sync.eth.wait_for_transaction_receipt(tx_hash)
        )

        if receipt.status == 1:
            return tx_hash.hex()
        else:
            raise Exception(
                f"Failed to mint soul: {tx_hash.hex()} | Network: {network}"
            )

    def process_mint_transaction(
        self, mint_data: MintSoulData, network: Literal["OP", "ZK", "LINEA"]
    ):
        if network == "LINEA":
            return self.create_transaction_for_linea(mint_data)

        transaction_data = self.build_transaction_data(mint_data)

        gas_price = (
            self.op_bnb.eth.gas_price
            if network == "OP"
            else (
                self.zk_sync.eth.gas_price
                if network == "ZK"
                else self.linea.eth.gas_price
            )
        )

        nonce = (
            self.op_bnb.eth.get_transaction_count(self.address)
            if network == "OP"
            else (
                self.zk_sync.eth.get_transaction_count(self.address)
                if network == "ZK"
                else self.linea.eth.get_transaction_count(self.address)
            )
        )

        transaction = {
            "to": mint_data.contract,
            "data": transaction_data,
            "gas": int(gas_price * 1.2),
            "gasPrice": gas_price,
            "nonce": nonce,
            "value": 0,
        }

        return self.sign_transaction(transaction, network)
