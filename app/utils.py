import httpx
import asyncio
import random
from typing import Dict, List, Optional
from urllib.parse import urlencode

SCAN_API_URL = "https://scan.rss3.io/api"
MAX_RETRIES = 5
UNSTAKE_TOPIC = "0x2808f92d5a0fada467cbe4e766f62f323e78271a7471058a87ef63a9e3e4c5c5"
BRIDGE_WITHDRAWAL_TOPIC = "0x73d170910aba9e6d50b102db522b1dbcd796216f5128b445aa2135272886497e"

async def get_latest_block_number() -> int:
    url = f"{SCAN_API_URL}?module=block&action=eth_block_number"
    print(f"Requesting URL: {url}")
    for _ in range(MAX_RETRIES):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            if "Something went wrong" not in str(data):
                await random_sleep()
                return int(data['result'], 16)
        print("Error getting latest block number. Retrying...")
        await random_sleep()
    raise Exception("Failed to get latest block number after multiple retries")

async def fetch_unstake_logs(from_block: int, to_block: int) -> List[Dict]:
    params = {
        "module": "logs",
        "action": "getLogs",
        "fromBlock": from_block,
        "toBlock": to_block,
        "address": "0x28F14d917fddbA0c1f2923C406952478DfDA5578",
        "topic0": UNSTAKE_TOPIC
    }
    url = f"{SCAN_API_URL}?{urlencode(params)}"
    print(f"Requesting URL: {url}")
    for _ in range(MAX_RETRIES):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            if "No logs found" in str(data):
                print("No logs found")

            if "Something went wrong" not in str(data):
                await random_sleep()
                return data['result']
        print(f"Error fetching unstake logs for blocks {from_block} to {to_block}. Retrying...")
        await random_sleep()
    raise Exception(f"Failed to fetch unstake logs for blocks {from_block} to {to_block} after multiple retries")

def parse_unstake_log(log: Dict) -> Optional[Dict]:
    if log['topics'][0] != UNSTAKE_TOPIC:
        return None
    
    user_address = "0x" + log['topics'][1][-40:]
    node_address = "0x" + log['topics'][2][-40:]
    amount = int(log['data'][0:66], 16)
    return {
        "tx_hash": log['transactionHash'],
        "node_address": node_address,
        "user_address": user_address,
        "amount": amount
    }

async def random_sleep():
    pass

async def fetch_bridge_withdrawal_logs(from_block: int, to_block: int) -> List[Dict]:
    params = {
        "module": "logs",
        "action": "getLogs",
        "fromBlock": from_block,
        "toBlock": to_block,
        "address": "0x4200000000000000000000000000000000000010",
        "topic0": BRIDGE_WITHDRAWAL_TOPIC
    }
    url = f"{SCAN_API_URL}?{urlencode(params)}"
    print(f"Requesting URL: {url}")
    for _ in range(MAX_RETRIES):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            if "No logs found" in str(data):
                print("No logs found")

            if "Something went wrong" not in str(data):
                await random_sleep()
                return data['result']
        print(f"Error fetching bridge withdrawal logs for blocks {from_block} to {to_block}. Retrying...")
        await random_sleep()
    raise Exception(f"Failed to fetch bridge withdrawal logs for blocks {from_block} to {to_block} after multiple retries")

def parse_bridge_withdrawal_log(log: Dict) -> Optional[Dict]:
    if log['topics'][0] != BRIDGE_WITHDRAWAL_TOPIC:
        return None
    
    user_address = "0x" + log['topics'][3][-40:]
    amount = int(log['data'][66:130], 16)  # 第2个bytes32
    return {
        "tx_hash": log['transactionHash'],
        "user_address": user_address,
        "amount": amount
    }