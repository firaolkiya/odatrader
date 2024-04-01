"""WebSocket price stream."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/prices/{symbol}")
async def price_stream(websocket: WebSocket, symbol: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"symbol": symbol, "echo": data, "source": "OdaTrade"})
    except WebSocketDisconnect:
        pass
