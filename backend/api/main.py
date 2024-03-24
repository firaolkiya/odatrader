# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import threading

app = FastAPI()

# Global state to track if the bot is running
bot_state = {"bot_running": False, "bot_process": None}


@app.get("/status")
def get_status():
    return {"bot_running": bot_state["bot_running"]}


@app.post("/start")
def start_bot():
    if not bot_state["bot_running"]:
        def run_bot():
            bot_state["bot_process"] = subprocess.Popen(["python", "scalping_bot_framework.py"])
            bot_state["bot_process"].wait()
            bot_state["bot_running"] = False  # Reset when bot exits

        threading.Thread(target=run_bot, daemon=True).start()
        bot_state["bot_running"] = True
        return {"status": "Bot started"}
    else:
        return {"status": "Bot already running"}


@app.post("/stop")
def stop_bot():
    if bot_state["bot_running"] and bot_state["bot_process"]:
        bot_state["bot_process"].terminate()
        bot_state["bot_running"] = False
        return {"status": "Bot stopped"}
    return {"status": "Bot is not running"}
