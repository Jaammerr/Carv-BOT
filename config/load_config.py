import os
import yaml

from loguru import logger
from models import Account, Config


def get_accounts() -> Account:
    accounts_path = os.path.join(os.path.dirname(__file__), "accounts.txt")
    if not os.path.exists(accounts_path):
        logger.error(f"File <<{accounts_path}>> does not exist")
        exit(1)

    with open(accounts_path, "r") as f:
        accounts = f.readlines()

        if not accounts:
            logger.error(f"File <<{accounts_path}>> is empty")
            exit(1)

        for account in accounts:
            values = account.split("|")
            if len(values) == 2:
                yield Account(pk_or_mnemonic=values[0].strip(), proxy=values[1].strip())

            else:
                logger.error(
                    f"Account <<{account}>> is not in correct format | Need to be in format: <<auth_token|mnemonic|proxy>>"
                )
                exit(1)


def load_config() -> Config:
    settings_path = os.path.join(os.path.dirname(__file__), "settings.yaml")
    if not os.path.exists(settings_path):
        logger.error(f"File <<{settings_path}>> does not exist")
        exit(1)

    with open(settings_path, "r") as f:
        settings = yaml.safe_load(f)

    if not settings.get("op_rpc"):
        logger.error(f"OP RPC is not provided in settings.yaml")
        exit(1)

    if not settings.get("zk_rpc"):
        logger.error(f"ZK RPC is not provided in settings.yaml")
        exit(1)

    if not settings.get("linea_rpc"):
        logger.error(f"LINEA RPC is not provided in settings.yaml")
        exit(1)

    return Config(
        accounts=list(get_accounts()),
        networks=settings.get("networks"),
        op_rpc=settings.get("op_rpc"),
        zk_rpc=settings.get("zk_rpc"),
        linea_rpc=settings.get("linea_rpc"),
    )
