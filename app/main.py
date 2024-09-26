#!/usr/bin/env python3

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .scanner import CombinedScanner
from .utils import get_latest_block_number

app = FastAPI()
templates = Jinja2Templates(directory="templates")

scanner = CombinedScanner()

@app.on_event("startup")
async def startup_event():
    latest_block = await get_latest_block_number()
    await scanner.start_scanning(latest_block)

@app.get("/node_statistics")
async def get_node_statistics():
    latest_block = await get_latest_block_number()
    print("latest block:", latest_block)
    await scanner.start_scanning(latest_block)
    return await scanner.get_node_statistics()

@app.get("/user_statistics")
async def get_user_statistics():
    latest_block = await get_latest_block_number()
    print("latest block:", latest_block)
    await scanner.start_scanning(latest_block)
    return await scanner.get_user_statistics()

@app.get("/", response_class=HTMLResponse)
async def chart(request: Request):
    latest_block = await get_latest_block_number()
    print("latest block:", latest_block)
    await scanner.start_scanning(latest_block)
    return templates.TemplateResponse("chart.html", {"request": request})

@app.get("/rescan")
async def rescan(background_tasks: BackgroundTasks):
    latest_block = await get_latest_block_number()
    background_tasks.add_task(scanner.start_scanning, latest_block)
    return {"message": "Rescan initiated"}