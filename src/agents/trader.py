"""Simplified trader agent using OpenAI function calling"""
import os
import json
import sys
from typing import List, Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.accounts import Account
from core.market import get_share_price
from core.database import write_log
from agents.templates import trader_instructions, trade_message, rebalance

_message

load_dotenv()

# Trader strategies
STRATEGIES = {
    "Warren": """Value Investing Strategy:
- Focus on fundamentally strong companies trading below intrinsic value
- Long-term holds (6-12 months minimum)
- Prefer dividend-paying stocks and established companies
- Buy when others are fearful, be patient
- Target: Steady 15-20% annual returns""",
    
    "George": """Momentum Trading Strategy:
- Capitalize on strong price momentum and market trends
- Quick entries and exits (hold days to weeks)
- Use technical indicators and price action
- Cut losses fast, let winners run
- Target: High turnover, 25-30% annual returns""",
    
    "Ray": """Systematic Quantitative Strategy:
- Rules-based approach using technical indicators
- Diversified portfolio across sectors
- Strict risk management with stop-losses
- Rebalance monthly based on signals
- Target: Consistent 18-22% annual returns""",
    
    "Cathie": """Growth & Innovation Strategy:
- Invest in disruptive technologies and future trends
- High conviction in transformative companies
- Accept volatility for exponential upside
- Focus on AI, biotech, clean energy, fintech
- Target: 30-40% annual returns (high risk)"""
}


class SimpleTrader:
    """Simplified trader using OpenAI function calling"""
    
    def __init__(self, name: str, model_name: str):
        self.name = name
        self.model_name = model_name
        self.account = Account.get(name)
        self.do_trade = True  # Alternate between trading and rebalancing
        
        # Initialize with strategy if new account
        if not self.account.strategy:
            self.account.strategy = STRATEGIES.get(name, "")
            self.account.save()
        
        # Setup OpenAI client based on model
        if "deepseek" in model_name.lower():
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY")
            )
        else:
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY")
            )
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for the trader"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_share_price",
                    "description": "Get current price of a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock ticker symbol (e.g., AAPL, TSLA, GOOGL)"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "buy_shares",
                    "description": "Buy shares of a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "Stock ticker"},
                            "quantity": {"type": "integer", "description": "Number of shares"},
                            "rationale": {"type": "string", "description": "Why buying"}
                        },
                        "required": ["symbol", "quantity", "rationale"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "sell_shares",
                    "description": "Sell shares of a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "Stock ticker"},
                            "quantity": {"type": "integer", "description": "Number of shares"},
                            "rationale": {"type": "string", "description": "Why selling"}
                        },
                        "required": ["symbol", "quantity", "rationale"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_account",
                    "description": "Get current account status (balance, holdings, P&L)",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool and return result"""
        try:
            if tool_name == "get_share_price":
                price = get_share_price(arguments["symbol"])
                return f"${price:.2f}"
            
            elif tool_name == "buy_shares":
                result = self.account.buy_shares(
                    arguments["symbol"],
                    arguments["quantity"],
                    arguments["rationale"]
                )
                return result
            
            elif tool_name == "sell_shares":
                result = self.account.sell_shares(
                    arguments["symbol"],
                    arguments["quantity"],
                    arguments["rationale"]
                )
                return result
            
            elif tool_name == "get_account":
                return self.account.report()
            
            else:
                return f"Unknown tool: {tool_name}"
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def run(self, max_turns: int = 10):
        """Run the trader agent"""
        try:
            write_log(self.name, "agent", f"Starting {'trading' if self.do_trade else 'rebalancing'} session")
            
            # Get initial message
            message = (
                trade_message(self.name, self.account.strategy, self.account.report())
                if self.do_trade
                else rebalance_message(self.name, self.account.strategy, self.account.report())
            )
            
            messages = [
                {"role": "system", "content": trader_instructions(self.name)},
                {"role": "user", "content": message}
            ]
            
            # Agent loop
            for turn in range(max_turns):
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=self.get_tools(),
                    tool_choice="auto"
                )
                
                assistant_message = response.choices[0].message
                messages.append(assistant_message.model_dump())
                
                # Check if done
                if not assistant_message.tool_calls:
                    write_log(self.name, "response", assistant_message.content or "No response")
                    print(f"{self.name}: {assistant_message.content}")
                    break
                
                # Execute tools
                for tool_call in assistant_message.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    write_log(self.name, "function", f"{func_name}({args})")
                    result = await self.execute_tool(func_name, args)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
            
            # Toggle mode for next run
            self.do_trade = not self.do_trade
            write_log(self.name, "agent", "Session complete")
            
        except Exception as e:
            write_log(self.name, "error", str(e))
            print(f"{self.name} error: {e}")
