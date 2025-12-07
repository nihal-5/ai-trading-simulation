"""Trading floor orchestrator - runs all traders"""
import asyncio
import os
import sys
from typing import List
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
from src.agents.trader import SimpleTrader

load_dotenv()

USE_MANY_MODELS = os.getenv("USE_MANY_MODELS", "false").lower() == "true"
RUN_EVERY_N_MINUTES = int(os.getenv("RUN_EVERY_N_MINUTES", "60"))

# Trader configurations
TRADERS = [
    {"name": "Warren", "model": "openai/gpt-4o-mini"},
    {"name": "George", "model": "deepseek/deepseek-chat"},
    {"name": "Ray", "model": "openai/gpt-4o-mini"},
    {"name": "Cathie", "model": "deepseek/deepseek-chat"}
]


def create_traders() -> List[SimpleTrader]:
    """Create all trader instances"""
    traders = []
    for config in TRADERS:
        trader = SimpleTrader(config["name"], config["model"])
        traders.append(trader)
    return traders


async def run_trading_session():
    """Run one trading session for all traders"""
    traders = create_traders()
    
    print("\n" + "="*60)
    print("🏦 AI TRADING SIMULATION - Session Starting")
    print("="*60 + "\n")
    
    # Run all traders in parallel
    await asyncio.gather(*[trader.run() for trader in traders])
    
    print("\n" + "="*60)
    print("✅ Session Complete")
    print("="*60 + "\n")


async def run_continuous():
    """Run trading sessions continuously"""
    while True:
        await run_trading_session()
        print(f"\n⏰ Next session in {RUN_EVERY_N_MINUTES} minutes...\n")
        await asyncio.sleep(RUN_EVERY_N_MINUTES * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run once for testing
        asyncio.run(run_trading_session())
    else:
        # Run continuously
        print(f"Starting trading floor (sessions every {RUN_EVERY_N_MINUTES} minutes)")
        print("Press Ctrl+C to stop\n")
        asyncio.run(run_continuous())
