from pydantic import BaseModel


class MintSoulData(BaseModel):

    class Permit(BaseModel):
        account: str
        amount: int
        ymd: int

    permit: Permit
    signature: str
    contract: str
    chain_id: int
    tx_hash: str = None


class RewardsList(BaseModel):

    class Reward(BaseModel):
        id: int
        description: str
        soul_count: int
        is_countdown: bool
        countdown_timestamp: int

    data_rewards: list[Reward] | None = None
