from fastapi import APIRouter, HTTPException
import os

router = APIRouter()
FLAG_PATH = "backend/risk/kill_switch.flag"

@router.post("/kill-switch/on")
def activate_kill_switch():
    try:
        with open(FLAG_PATH, "w") as f:
            f.write("KILL")
        return {"status": "success", "message": "🚨 Kill switch activated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kill-switch/off")
def deactivate_kill_switch():
    try:
        if os.path.exists(FLAG_PATH):
            os.remove(FLAG_PATH)
        return {"status": "success", "message": "✅ Kill switch deactivated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kill-switch/status")
def check_kill_switch():
    if os.path.exists(FLAG_PATH):
        return {"kill_switch": True, "message": "🚨 Active"}
    return {"kill_switch": False, "message": "✅ Not active"}
