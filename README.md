# AI Trading Simulation

> Watch 4 different AI models compete against each other as stock traders. Each has its own personality and strategy.

## 🚀 Live Demo

**[View in AI Portfolio Dashboard](https://unharmable-threadlike-ruth.ngrok-free.dev)** | **[Direct Access](https://unharmable-threadlike-ruth.ngrok-free.dev:8001)**

> Part of **[Nihal's AI Portfolio](https://unharmable-threadlike-ruth.ngrok-free.dev)** - Unified dashboard featuring 5 cutting-edge AI services

I built this because I was curious: if you gave AI traders different strategies and let them loose on the stock market, who would win? Turns out, watching Warren (the value investor) battle against Cathie (the growth/disruption trader) is pretty fun.

## What is this?

Four AI-powered traders compete in a simulated stock market:
- They use **real stock prices** from Polygon.io
- Each trader has its **own strategy** (value investing vs momentum vs growth etc.)
- They run on **different AI models** (GPT-4, Gemini, Deepseek) to see which reasons better
- A dashboard shows their portfolios, decisions, and P&L in real-time

Think of it like a trading competition, except the contestants are AI.

## The Traders

**Warren** - The patient value investor (GPT-4)
- Looks for undervalued companies with solid fundamentals
- Buys and holds for the long term
- Conservative but steady

**George** - The momentum chaser (Gemini 2.0)  
- Jumps on trending stocks
- In and out quickly to catch the wave
- High risk, high reward

**Ray** - The systematic quant (Deepseek)
- Uses technical indicators and rules
- Diversifies across sectors
- Disciplined rebalancing

**Cathie** - The innovation hunter (GPT-4)
- All-in on disruptive tech (AI, biotech, clean energy)
- High conviction, accepts volatility
- Swings for the fences

## Setup

```bash
git clone https://github.com/nihal-5/ai-trading-simulation.git
cd ai-trading-simulation

pip install -r requirements.txt

cp .env.example .env
# Add your API keys to .env
```

**API keys you'll need:**
- OpenAI (required) - https://platform.openai.com
- Polygon.io (optional, for real prices) - https://polygon.io  
- Brave Search (optional) - https://brave.com/search/api

Without Polygon, it'll use random simulated prices. Still works fine for testing.

## Running It

**Start the dashboard:**
```bash
python dashboard.py
```

Open https://unharmable-threadlike-ruth.ngrok-free.dev:7860 in your browser.

**To make the traders trade:**
- Click the big "▶️ Run Trading Session" button in the dashboard
- Wait ~2 minutes while they analyze and trade
- Click refresh on each trader's tab to see what they did

Each trader independently:
1. Analyzes the current market
2. Checks their portfolio
3. Decides what to buy/sell based on their strategy
4. Executes trades
5. Explains their reasoning

## What I learned building this

- **Different AI models actually think differently** - GPT-4 is more cautious, Gemini is more aggressive, Deepseek is very methodical
- **Function calling is powerful** - the agents can look up prices, check portfolios, execute trades, all autonomously
- **Strategy matters more than model** - a good strategy on a cheaper model beats a bad strategy on an expensive one
- **Gradio makes dashboards stupid easy** - went from code to visual dashboard in like an hour

## Tech Stack

- **Python** for everything
- **OpenAI, Gemini, Deepseek** for the AI traders
- **Gradio** for the dashboard (so much easier than building a React app)
- **Plotly** for the charts
- **SQLite** for storing trades and portfolio history
- **Polygon API** for real stock prices

## Current Results

After a few trading sessions:
- Warren is up ~2% (slow and steady)
- Cathie is down ~0.2% (swing for the fences, some misses)
- Ray held AAPL, sold some for rebalancing
- George is analyzing but hasn't made big moves yet

The interesting part isn't who's winning, it's watching their different approaches play out.

## Future Ideas

- Add more traders with different strategies
- Backtest against historical data
- Add risk limits (max position size, stop losses)
- Email alerts when big trades happen
- Track which AI model performs best over time

## Why I Built This

I wanted to:
1. Learn multi-agent AI systems
2. See if different AI models make different trading decisions
3. Build something actually fun to watch
4. Practice system design (agents, tools, database, UI, APIs)

Turns out it's addictive to watch AI traders compete. Who knew?

## License

MIT - do whatever you want with it

## Questions?

Open an issue or find me [@nihal-5](https://github.com/nihal-5)

---

**Note:** This is a simulation. Don't use it for real trading. The AI traders are autonomous and will make decisions you might not agree with. That's the whole point.
