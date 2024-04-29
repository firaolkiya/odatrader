"""Instruments and subscription API."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from backend.auth.middleware import require_auth
from backend.core.instruments import instrument_service, AssetClass

router = APIRouter(prefix="/instruments", tags=["instruments"])

_subscriptions: dict = {}


class SubscribeRequest(BaseModel):
    symbol: str
    streams: List[str] = ["trades", "quotes", "bars"]
    timeframe: str = "1m"


@router.get("/")
def list_instruments(asset_class: Optional[str] = None):
    instrument_service.load_from_yaml()
    instruments = instrument_service.list_all()
    if asset_class:
        try:
            ac = AssetClass(asset_class)
            instruments = instrument_service.list_by_class(ac)
        except ValueError:
            pass
    return {"instruments": [i.to_dict() for i in instruments]}


@router.get("/{symbol}")
def get_instrument(symbol: str):
    inst = instrument_service.get(symbol)
    if not inst:
        return {"error": "not found"}
    return inst.to_dict()


@router.post("/subscribe", dependencies=[Depends(require_auth)])
async def subscribe(req: SubscribeRequest):
    inst = instrument_service.get(req.symbol)
    if not inst:
        return {"error": f"Unknown instrument: {req.symbol}"}
    from backend.gateway.factory import get_gateway
    gw = get_gateway(inst)
    await gw.connect()
    _subscriptions[req.symbol] = {"streams": req.streams, "timeframe": req.timeframe, "gateway": inst.venue}
    return {"subscribed": req.symbol, "streams": req.streams, "venue": inst.venue}


@router.get("/pairs/scores")
def pair_scores():
    from backend.engine.pair_scorer import PairScorer
    scorer = PairScorer()
    instrument_service.load_from_yaml()
    for inst in instrument_service.list_all():
        scorer.update_metadata(inst.symbol, volume=1e6, spread=0.0005, vol=0.02, depth=10000,
                               funding_rate=inst.funding_rate)
    return {"scores": scorer.score_all(), "top_k": scorer.get_top_k()}
