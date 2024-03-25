from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import subprocess
import threading
import os ,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.config import BINANCE_SECRET_KEY


app = FastAPI()

# Global state to track if the bot is running
bot_state = {"bot_running": False, "bot_process": None}
KILL_SWITCH_PATH = "backend/risk/kill_switch.flag"
API_SECRET_KEY = f"{BINANCE_SECRET_KEY}"  # fallback for local dev


@app.get("/status")
def get_status():
    return {
        "bot_running": bot_state["bot_running"],
        "kill_switch": os.path.exists(KILL_SWITCH_PATH)
    }


@app.post("/start")
def start_bot():
    if os.path.exists(KILL_SWITCH_PATH):
        return {"status": "❌ Cannot start — Kill switch is active."}

    if not bot_state["bot_running"]:
        def run_bot():
            bot_state["bot_process"] = subprocess.Popen(["python", "scalping_bot_framework.py"])
            bot_state["bot_process"].wait()
            bot_state["bot_running"] = False  # Reset when bot exits

        threading.Thread(target=run_bot, daemon=True).start()
        bot_state["bot_running"] = True
        return {"status": "✅ Bot started"}
    else:
        return {"status": "ℹ️ Bot already running"}


@app.post("/stop")
def stop_bot():
    if bot_state["bot_running"] and bot_state["bot_process"]:
        bot_state["bot_process"].terminate()
        bot_state["bot_running"] = False
        return {"status": "🛑 Bot stopped"}
    return {"status": "ℹ️ Bot is not running"}


# ==== KILL SWITCH ROUTES ==== #

@app.post("/kill-switch/on")
def activate_kill_switch(x_api_key: str = Header(...)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    try:
        with open(KILL_SWITCH_PATH, "w") as f:
            f.write("KILL")
        return {"status": "🚨 Kill switch activated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kill-switch/off")
def deactivate_kill_switch(x_api_key: str = Header(...)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    try:
        if os.path.exists(KILL_SWITCH_PATH):
            os.remove(KILL_SWITCH_PATH)
        return {"status": "✅ Kill switch deactivated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/kill-switch/status")
def check_kill_switch():
    if os.path.exists(KILL_SWITCH_PATH):
        return {"kill_switch": True, "message": "🚨 Active"}
    return {"kill_switch": False, "message": "✅ Not active"}
