import asyncio
import json
import os
from typing import Dict, List
from .utils import fetch_logs, parse_log
from .models import ScanResult

class Scanner:
    def __init__(self):
        self.results: Dict[str, ScanResult] = {}
        self.start_block = 7351004
        self.block_interval = 20000
        self.results_file = "scan_results.json"
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
        print("start block: ", self.start_block)
        if self.start_block == 0:
            self.start_block = latest_block - 10000  # Start from 10000 blocks ago if no previous progress

        while True:
            end_block = min(self.start_block + self.block_interval, latest_block)
            logs = await fetch_logs(self.start_block, end_block)
            print("fetch logs: [", self.start_block, " - ", end_block, "]","count: ", len(logs))

            for log in logs:
                parsed_log = parse_log(log)
                if parsed_log:  # Only update results if parsed_log is not None
                    self.update_results(parsed_log)
            
            self.start_block = end_block + 1
            self.save_results()  # Save progress after each interval

            if self.start_block > latest_block:
                print("scan block end")
                break
            
    def update_results(self, log: Dict):
        node_address = log['node_address']
        if node_address not in self.results:
            self.results[node_address] = ScanResult(address=node_address, total_amount=0, total_count=0)
        
        self.results[node_address].total_amount += log['amount']
        self.results[node_address].total_count += 1

    async def get_statistics(self):
        total_count = sum(result.total_count for result in self.results.values())
        total_amount = sum(result.total_amount for result in self.results.values())
        return {
            "results": list(self.results.values()),
            "total_count": total_count,
            "total_amount": int(total_amount)
        }