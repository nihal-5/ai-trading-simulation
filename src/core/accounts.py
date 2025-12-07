"""Trading account management with buy/sell operations"""
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime
import json
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.market import get_share_price
from core.database import write_account, read_account, write_log

INITIAL_BALANCE = float(os.getenv("INITIAL_BALANCE", "10000"))
SPREAD = 0.002  # 0.2% spread on trades


class Transaction(BaseModel):
    """Single transaction record"""
    symbol: str
    quantity: int  # Positive for buy, negative for sell
    price: float
    timestamp: str
    rationale: str
    
    def total(self) -> float:
        return abs(self.quantity) * self.price
    
    def __repr__(self):
        action = "bought" if self.quantity > 0 else "sold"
        return f"{action} {abs(self.quantity)} shares of {self.symbol} at ${self.price:.2f}"


class Account(BaseModel):
    """Trading account for a single trader"""
    name: str
    balance: float
    strategy: str
    holdings: Dict[str, int]
    transactions: List[Transaction]
    portfolio_value_time_series: List[tuple]
    
    @classmethod
    def get(cls, name: str):
        """Load or create account"""
        fields = read_account(name.lower())
        if not fields:
            fields = {
                "name": name.lower(),
                "balance": INITIAL_BALANCE,
                "strategy": "",
                "holdings": {},
                "transactions": [],
                "portfolio_value_time_series": []
            }
            write_account(name.lower(), fields)
        return cls(**fields)
    
    def save(self):
        """Persist account to database"""
        write_account(self.name.lower(), self.model_dump())
    
    def reset(self, strategy: str):
        """Reset account with new strategy"""
        self.balance = INITIAL_BALANCE
        self.strategy = strategy
        self.holdings = {}
        self.transactions = []
        self.portfolio_value_time_series = []
        self.save()
    
    def buy_shares(self, symbol: str, quantity: int, rationale: str) -> str:
        """Buy shares with spread"""
        price = get_share_price(symbol)
        if price == 0:
            raise ValueError(f"Invalid symbol: {symbol}")
        
        buy_price = price * (1 + SPREAD)
        total_cost = buy_price * quantity
        
        if total_cost > self.balance:
            raise ValueError(f"Insufficient funds. Need ${total_cost:.2f}, have ${self.balance:.2f}")
        
        # Update holdings
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        
        # Record transaction
        transaction = Transaction(
            symbol=symbol,
            quantity=quantity,
            price=buy_price,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            rationale=rationale
        )
        self.transactions.append(transaction)
        
        # Update balance
        self.balance -= total_cost
        self.save()
        write_log(self.name, "account", f"Bought {quantity} {symbol} @ ${buy_price:.2f}")
        
        return f"✅ Purchased {quantity} shares of {symbol} at ${buy_price:.2f}. New balance: ${self.balance:.2f}"
    
    def sell_shares(self, symbol: str, quantity: int, rationale: str) -> str:
        """Sell shares with spread"""
        if self.holdings.get(symbol, 0) < quantity:
            raise ValueError(f"Cannot sell {quantity} shares of {symbol}. Only have {self.holdings.get(symbol, 0)}")
        
        price = get_share_price(symbol)
        sell_price = price * (1 - SPREAD)
        total_proceeds = sell_price * quantity
        
        # Update holdings
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        
        # Record transaction
        transaction = Transaction(
            symbol=symbol,
            quantity=-quantity,  # Negative for sell
            price=sell_price,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            rationale=rationale
        )
        self.transactions.append(transaction)
        
        # Update balance
        self.balance += total_proceeds
        self.save()
        write_log(self.name, "account", f"Sold {quantity} {symbol} @ ${sell_price:.2f}")
        
        return f"✅ Sold {quantity} shares of {symbol} at ${sell_price:.2f}. New balance: ${self.balance:.2f}"
    
    def calculate_portfolio_value(self) -> float:
        """Calculate total portfolio value (cash + holdings)"""
        total = self.balance
        for symbol, quantity in self.holdings.items():
            total += get_share_price(symbol) * quantity
        return total
    
    def calculate_profit_loss(self, portfolio_value: float = None) -> float:
        """Calculate P&L from initial investment"""
        if portfolio_value is None:
            portfolio_value = self.calculate_portfolio_value()
        return portfolio_value - INITIAL_BALANCE
    
    def get_holdings(self) -> Dict[str, int]:
        """Get current holdings"""
        return self.holdings
    
    def list_transactions(self) -> List[dict]:
        """Get transaction history"""
        return [t.model_dump() for t in self.transactions]
    
    def report(self) -> str:
        """Generate account report as JSON"""
        portfolio_value = self.calculate_portfolio_value()
        pnl = self.calculate_profit_loss(portfolio_value)
        
        # Record portfolio value
        self.portfolio_value_time_series.append(
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), portfolio_value)
        )
        self.save()
        
        data = self.model_dump()
        data["total_portfolio_value"] = portfolio_value
        data["total_profit_loss"] = pnl
        write_log(self.name, "account", "Retrieved account report")
        
        return json.dumps(data, indent=2)
    
    def get_strategy(self) -> str:
        """Get current strategy"""
        return self.strategy
    
    def change_strategy(self, strategy: str) -> str:
        """Update trading strategy"""
        self.strategy = strategy
        self.save()
        write_log(self.name, "account", "Changed strategy")
        return f"✅ Strategy updated"
