from pydantic import BaseModel
from typing import List

class ScanResult(BaseModel):
    address: str
    total_amount: int
    total_count: int

class StatisticsResponse(BaseModel):
    results: List[ScanResult]
    total_count: int
    total_amount: int