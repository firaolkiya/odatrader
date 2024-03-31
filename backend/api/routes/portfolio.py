"""Portfolio API routes."""
from fastapi import APIRouter
from backend.portfolio.tracker import PortfolioTracker

router = APIRouter(prefix="/portfolio", tags=["portfolio"])
tracker = PortfolioTracker()

@router.get("/summary")
def portfolio_summary():
    return tracker.get_summary()

@router.get("/positions")
def positions():
    return tracker.get_positions()
