from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from .scanner import Scanner
from .models import ScanResult, StatisticsResponse
from .utils import get_latest_block_number

app = FastAPI()
templates = Jinja2Templates(directory="templates")

scanner = Scanner()

@app.on_event("startup")
async def startup_event():
    latest_block = await get_latest_block_number()
    await scanner.start_scanning(latest_block)

@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    latest_block = await get_latest_block_number()
    print("latest block:", latest_block)
    await scanner.start_scanning(latest_block)
    return await scanner.get_statistics()

@app.get("/", response_class=HTMLResponse)
async def chart(request: Request):
    return templates.TemplateResponse("chart.html", {"request": request})

@app.get("/rescan")
async def rescan(background_tasks: BackgroundTasks):
    latest_block = await get_latest_block_number()
    background_tasks.add_task(scanner.start_scanning, latest_block)
    return {"message": "Rescan initiated"}