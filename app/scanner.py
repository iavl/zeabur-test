import asyncio
import json
import os
from typing import Dict, List
from .utils import fetch_unstake_logs, parse_unstake_log, fetch_bridge_withdrawal_logs, parse_bridge_withdrawal_log
from .models import ScanResult, StatisticsResponse

class BaseScanner:
    def __init__(self, results_file: str):
        self.results: Dict[str, ScanResult] = {}
        self.start_block = 7351004
        self.block_interval = 20000
        self.results_file = results_file
        self.load_results()

    def load_results(self):
        if os.path.exists(self.results_file):
            with open(self.results_file, "r") as f:
                data = json.load(f)
                self.start_block = data["last_scanned_block"]
                self.results = {
                    address: ScanResult(**result)
                    for address, result in data["results"].items()
                }
        else:
            self.start_block = 7351004

    def save_results(self):
        data = {
            "last_scanned_block": self.start_block,
            "results": {
                address: result.dict()
                for address, result in self.results.items()
            }
        }
        with open(self.results_file, "w") as f:
            json.dump(data, f)

    async def start_scanning(self, latest_block: int):
        print(f"Start scanning {self.__class__.__name__} from block: {self.start_block}")
        if self.start_block == 0:
            self.start_block = latest_block - 10000

        while True:
            end_block = min(self.start_block + self.block_interval, latest_block)
            logs = await fetch_unstake_logs(self.start_block, end_block)
            print(f"Fetch unstake logs for {self.__class__.__name__}: [{self.start_block} - {end_block}], count: {len(logs)}")

            for log in logs:
                parsed_log = parse_unstake_log(log)
                if parsed_log:
                    self.update_results(parsed_log)
            
            self.start_block = end_block + 1
            self.save_results()

            if self.start_block > latest_block:
                print(f"Scan block end for {self.__class__.__name__}")
                break

    def update_results(self, log: Dict):
        raise NotImplementedError("Subclasses must implement this method")

    async def get_statistics(self):
        total_count = sum(result.total_count for result in self.results.values())
        total_amount = sum(result.total_amount for result in self.results.values())
        return StatisticsResponse(
            results=list(self.results.values()),
            total_count=total_count,
            total_amount=int(total_amount)
        )

class NodeScanner(BaseScanner):
    def __init__(self):
        super().__init__("node_scan_results.json")

    def update_results(self, log: Dict):
        node_address = log['node_address']
        if node_address not in self.results:
            self.results[node_address] = ScanResult(address=node_address, total_amount=0, total_count=0)
        
        self.results[node_address].total_amount += log['amount']
        self.results[node_address].total_count += 1

class UserScanner(BaseScanner):
    def __init__(self):
        super().__init__("user_scan_results.json")

    def update_results(self, log: Dict):
        user_address = log['user_address']
        if user_address not in self.results:
            self.results[user_address] = ScanResult(address=user_address, total_amount=0, total_count=0)
        
        self.results[user_address].total_amount += log['amount']
        self.results[user_address].total_count += 1

class BridgeWithdrawalScanner(BaseScanner):
    def __init__(self):
        super().__init__("bridge_withdrawal_scan_results.json")

    async def start_scanning(self, latest_block: int):
        print(f"Start scanning {self.__class__.__name__} from block: {self.start_block}")
        if self.start_block == 0:
            self.start_block = latest_block - 10000

        while True:
            end_block = min(self.start_block + self.block_interval, latest_block)
            logs = await fetch_bridge_withdrawal_logs(self.start_block, end_block)
            print(f"Fetch logs for {self.__class__.__name__}: [{self.start_block} - {end_block}], count: {len(logs)}")

            for log in logs:
                parsed_log = parse_bridge_withdrawal_log(log)
                if parsed_log:
                    self.update_results(parsed_log)
            
            self.start_block = end_block + 1
            self.save_results()

            if self.start_block > latest_block:
                print(f"Scan block end for {self.__class__.__name__}")
                break

    def update_results(self, log: Dict):
        user_address = log['user_address']
        if user_address not in self.results:
            self.results[user_address] = ScanResult(address=user_address, total_amount=0, total_count=0)
        
        self.results[user_address].total_amount += log['amount']
        self.results[user_address].total_count += 1

class CombinedScanner:
    def __init__(self):
        self.node_scanner = NodeScanner()
        self.user_scanner = UserScanner()
        self.bridge_withdrawal_scanner = BridgeWithdrawalScanner()

    async def start_scanning(self, latest_block: int):
        await asyncio.gather(
            self.node_scanner.start_scanning(latest_block),
            self.user_scanner.start_scanning(latest_block),
            self.bridge_withdrawal_scanner.start_scanning(latest_block)
        )

    async def get_node_statistics(self):
        node_stats = await self.node_scanner.get_statistics()
        return {
            "results": node_stats.results,
            "total_count": node_stats.total_count,
            "total_amount": node_stats.total_amount
        }

    async def get_user_statistics(self):
        user_stats = await self.user_scanner.get_statistics()
        return {
            "results": user_stats.results,
            "total_count": user_stats.total_count,
            "total_amount": user_stats.total_amount
        }

    async def get_bridge_withdrawal_statistics(self):
        bridge_stats = await self.bridge_withdrawal_scanner.get_statistics()
        return {
            "results": bridge_stats.results,
            "total_count": bridge_stats.total_count,
            "total_amount": bridge_stats.total_amount
        }