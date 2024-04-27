
# MintChain Daily Bot

## 🔗 Links

🔔 CHANNEL: https://t.me/JamBitPY

💬 CHAT: https://t.me/JamBitChat

💰 DONATION EVM ADDRESS: 0xe23380ae575D990BebB3b81DB2F90Ce7eDbB6dDa


## 📝 | Description:
Every day at 04:30 the bot will mint SOUL in all networks that you specified and take away the available rewards.


## 🤖 | Features:

- **Auto mint SOUL (all networks)**
- **Auto claim rewards**


## 🚀 Installation

``Docker``


``1. Close the repo and open CMD (console) inside it``

``2. Setup configuration and accounts``

``3. Run: docker-compose up -d --build``

``OR``


`` Required python >= 3.10``

``1. Close the repo and open CMD (console) inside it``

``2. Install requirements: pip install -r requirements.txt``

``3. Setup configuration and accounts``

``4. Run: python run.py``


## ⚙️ Config (config > settings.yaml)

| Name | Description                                               |
| --- |-----------------------------------------------------------|
| networks | networks in which the script will mint SOUL               |
| op_rpc | OP BNB RPC URL (if not have, leave the default value)     |
| zk_rpc | ZKSYNC ERA RPC URL (if not have, leave the default value) |
| linea_rpc | LINEA RPC URL (if not have, leave the default value)      |


## ⚙️ Accounts format (config > accounts.txt)

- mnemonic (12-24 words)|proxy

``Example: "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12|jam.ip:3434:jam:1111"``

`` Proxy format: IP:PORT:USER:PASS``
