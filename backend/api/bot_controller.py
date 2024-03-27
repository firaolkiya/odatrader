from fastapi import FastAPI
from threading import Thread
import uvicorn
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scalping_bot_framework import run_bot, stop_bot

app = FastAPI()
bot_thread = None

@app.post("/start")
def start_bot_api():
    global bot_thread
    if bot_thread and bot_thread.is_alive():
        return {"status": "already running"}
    
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    return {"status": "started"}

@app.post("/stop")
def stop_bot_api():
    stop_bot()
    return {"status": "stopped"}

@app.get("/status")
def bot_status():
    from scalping_bot_framework import bot_running
    return {"running": bot_running}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
