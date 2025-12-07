"""Market data operations - Polygon.io integration with fallback to simulated data"""
import os
import random
from datetime import datetime, timezone
from functools import lru_cache
from typing import Dict
from dotenv import load_dotenv

# Import database after it's available
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.database import write_market, read_market

load_dotenv()

polygon_api_key = os.getenv("POLYGON_API_KEY")
polygon_plan = os.getenv("POLYGON_PLAN", "free")

is_paid_polygon = polygon_plan == "paid"
is_realtime_polygon = polygon_plan == "realtime"


def get_all_share_prices_polygon_eod() -> Dict[str, float]:
    """Get end-of-day prices from Polygon.io"""
    try:
        from polygon import RESTClient
        client = RESTClient(polygon_api_key)
        
        # Get last close date from SPY
        probe = client.get_previous_close_agg("SPY")[0]
        last_close = datetime.fromtimestamp(probe.timestamp / 1000, tz=timezone.utc).date()
        
        # Get all stock prices for that date
        results = client.get_grouped_daily_aggs(last_close, adjusted=True, include_otc=False)
        return {result.ticker: result.close for result in results}
    except Exception as e:
        print(f"Polygon API error: {e}")
        return {}


@lru_cache(maxsize=2)
def get_market_for_prior_date(today: str) -> Dict[str, float]:
    """Get or cache market data for a date"""
    market_data = read_market(today)
    if not market_data and polygon_api_key:
        market_data = get_all_share_prices_polygon_eod()
        if market_data:
            write_market(today, market_data)
    return market_data or {}


def get_share_price_polygon_eod(symbol: str) -> float:
    """Get share price from Polygon (end of day)"""
    today = datetime.now().date().strftime("%Y-%m-%d")
    market_data = get_market_for_prior_date(today)
    return market_data.get(symbol, 0.0)


def get_share_price_polygon_min(symbol: str) -> float:
    """Get share price from Polygon (15-min delay for paid tier)"""
    try:
        from polygon import RESTClient
        client = RESTClient(polygon_api_key)
        result = client.get_snapshot_ticker("stocks", symbol)
        return result.min.close or result.prev_day.close
    except:
        return 0.0


def get_share_price_polygon(symbol: str) -> float:
    """Get share price from Polygon based on plan"""
    if is_paid_polygon:
        return get_share_price_polygon_min(symbol)
    else:
        return get_share_price_polygon_eod(symbol)


def get_share_price(symbol: str) -> float:
    """Get share price with fallback to simulated data"""
    if polygon_api_key:
        try:
            price = get_share_price_polygon(symbol)
            if price > 0:
                return price
        except Exception as e:
            print(f"Polygon API failed for {symbol}: {e}")
    
    # Fallback: simulated prices (random but consistent per symbol)
    random.seed(hash(symbol + datetime.now().strftime("%Y-%m-%d")))
    return float(random.randint(10, 500))
