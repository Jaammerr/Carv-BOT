import dataclasses


@dataclasses.dataclass
class LineaContract:
    address: str = "0xC5Cb997016c9A3AC91cBe306e59B048a812C056f"
    abi: list = open("./abi/linea.json", "r").read()
