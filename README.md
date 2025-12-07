# AI Trading Simulation

Multi-agent AI trading simulation where 4 AI traders with different strategies compete in a simulated stock market using real-time data.

## Features

- 🤖 **4 AI Traders** with unique personalities and strategies
- 📊 **Real-Time Market Data** via Polygon.io
- 🔍 **AI Research Agent** using Brave Search
- 📈 **Live Dashboard** with Gradio (portfolio charts, holdings, transactions)
- 🎯 **MCP Architecture** (Model Context Protocol) for modular tools
- 💾 **Persistent State** with SQLite database

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your keys

# Run trading simulation
python trading_floor.py

# Launch dashboard (separate terminal)
python dashboard/app.py
```

Visit http://localhost:7860 to see the live dashboard!

## API Keys Required

- **OpenAI** - Get at https://platform.openai.com/api-keys
- **Polygon.io** (optional) - Get at https://polygon.io/ (or use simulated data)
- **Brave Search** (optional) - Get at https://brave.com/search/api/

## The Traders

### Warren "Patience"
- Strategy: Value investing, long-term holds
- Personality: Conservative, fundamentals-focused
- Model: GPT-4o-mini

### George "Bold"  
- Strategy: Momentum trading, quick profits
- Personality: Aggressive, high turnover
- Model: GPT-4o-mini

### Ray "Systematic"
- Strategy: Quantitative, rules-based
- Personality: Technical indicators, disciplined
- Model: GPT-4o-mini

### Cathie "Crypto"
- Strategy: Growth & innovation
- Personality: Disruptive tech, high conviction
- Model: GPT-4o-mini

## Architecture

```
┌─────────────────────────────────────────────────┐
│           Gradio Dashboard (Port 7860)          │
│      Portfolio Charts | Holdings | Logs         │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │ Trading Floor    │
        │  (Orchestrator)  │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┬────────────┐
    │            │            │            │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐   ┌───▼───┐
│Warren │   │George │   │  Ray  │   │Cathie │
│  AI   │   │  AI   │   │   AI  │   │   AI  │
└───┬───┘   └───┬───┘   └───┬───┘   └───┬───┘
    └────────────┼────────────┴────────────┘
                 │
        ┌────────▼────────┐
        │   MCP Servers   │
        │  (Accounts,     │
        │   Market, Push) │
        └─────────────────┘
```

## License

MIT

## Author

Built by [nihal-5](https://github.com/nihal-5)
