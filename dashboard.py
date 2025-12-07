"""Enhanced Gradio dashboard with all features from course project"""
import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from src.core.accounts import Account
from src.core.database import read_log


class TraderView:
    """Dashboard view for a single trader"""
    
    def __init__(self, name: str, model_name: str):
        self.name = name
        self.model_name = model_name
        self.account = Account.get(name)
    
    def reload(self):
        """Refresh account data"""
        self.account = Account.get(self.name)
    
    def get_portfolio_chart(self):
        """Generate portfolio value time series chart"""
        if not self.account.portfolio_value_time_series:
            fig = go.Figure()
            fig.add_annotation(
                text="No trading data yet",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="white")
            )
            fig.update_layout(
                height=250,
                paper_bgcolor="#2d2d2d",
                plot_bgcolor="#1a1a1a",
            )
            return fig
        
        df = pd.DataFrame(
            self.account.portfolio_value_time_series,
            columns=["datetime", "value"]
        )
        df["datetime"] = pd.to_datetime(df["datetime"])
        
        fig = px.line(df, x="datetime", y="value", title=f"{self.name}'s Portfolio")
        fig.update_layout(
            height=250,
            margin=dict(l=30, r=10, t=30, b=30),
            xaxis_title=None,
            yaxis_title="Value ($)",
            paper_bgcolor="#2d2d2d",
            plot_bgcolor="#1a1a1a",
            font=dict(color="white", size=12),
            title_font=dict(color="white", size=14)
        )
        fig.update_xaxes(tickformat="%m/%d %H:%M", tickangle=45, gridcolor="#444", tickfont=dict(size=10))
        fig.update_yaxes(tickformat="$,.0f", gridcolor="#444", tickfont=dict(size=10))
        fig.update_traces(line_color="#00ff88", line_width=2)
        return fig
    
    def get_portfolio_value_html(self):
        """Get portfolio value with P&L"""
        portfolio_value = self.account.calculate_portfolio_value()
        pnl = self.account.calculate_profit_loss(portfolio_value)
        
        color = "#10b981" if pnl >= 0 else "#ef4444"
        emoji = "📈" if pnl >= 0 else "📉"
        
        return f"""
        <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 10px;'>
            <h3 style='color: white; margin: 0; font-size: 18px;'>{self.name}</h3>
            <p style='color: #ddd; margin: 3px 0; font-size: 12px;'>{self.model_name}</p>
            <h2 style='color: white; margin: 8px 0; font-size: 24px;'>${portfolio_value:,.2f}</h2>
            <p style='color: {color}; font-size: 16px; margin: 0;'>{emoji} ${abs(pnl):,.2f} ({(pnl/10000)*100:+.1f}%)</p>
        </div>
        """
    
    def get_holdings_df(self):
        """Get holdings as DataFrame"""
        if not self.account.holdings:
            return pd.DataFrame(columns=["Symbol", "Shares"])
        
        from src.core.market import get_share_price
        return pd.DataFrame([
            {
                "Symbol": symbol, 
                "Shares": qty,
                "Price": f"${get_share_price(symbol):.2f}",
                "Value": f"${get_share_price(symbol) * qty:,.2f}"
            }
            for symbol, qty in self.account.holdings.items()
        ])
    
    def get_transactions_df(self):
        """Get recent transactions"""
        transactions = self.account.list_transactions()
        if not transactions:
            return pd.DataFrame(columns=["Time", "Action", "Symbol", "Qty", "Price"])
        
        recent = transactions[-10:]
        return pd.DataFrame([{
            "Time": t["timestamp"].split()[1] if " " in t["timestamp"] else t["timestamp"],
            "Action": "BUY" if t["quantity"] > 0 else "SELL",
            "Symbol": t["symbol"],
            "Qty": abs(t["quantity"]),
            "Price": f"${t['price']:.2f}",
        } for t in recent])
    
    def get_logs_html(self):
        """Get colored activity logs"""
        logs = read_log(self.name, last_n=20)
        
        colors = {
            "agent": "#00bcd4",
            "function": "#4caf50",
            "response": "#ff4081",
            "account": "#f44336",
            "error": "#ff5722"
        }
        
        html = "<div style='height: 150px; overflow-y: auto; background: #1a1a1a; padding: 8px; border-radius: 5px; font-family: monospace;'>"
        for timestamp, log_type, message in logs:
            color = colors.get(log_type, "#ffffff")
            html += f"<p style='color: {color}; margin: 2px 0; font-size: 11px;'>{timestamp} [{log_type}] {message[:80]}</p>"
        html += "</div>"
        return html


def create_dashboard():
    """Create the enhanced Gradio dashboard"""
    
    traders = [
        TraderView("Warren", "GPT-4o-mini"),
        TraderView("George", "Gemini 2.0"),
        TraderView("Ray", "Deepseek"),
        TraderView("Cathie", "GPT-4o-mini")
    ]
    
    with gr.Blocks(
        theme=gr.themes.Soft(primary_hue="purple"),
        title="AI Trading Simulation",
        css="""
        .gradio-container {background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);}
        .markdown h1, .markdown h2, .markdown h3, .markdown h4 {color: white !important;}
        .markdown p {color: #cccccc !important;}
        body, p, span, div, label {color: #ffffff !important;}
        .plotly .gtitle, .plotly text {fill: white !important; color: white !important;}
        .dataframe {color: #ffffff !important;}
        table {color: #ffffff !important;}
        button {color: #ffffff !important;}
        .tab-nav button {color: #ffffff !important;}
        """
    ) as dashboard:
        
        gr.Markdown("# 🏦 AI Trading Simulation Dashboard\n### Multi-agent trading with GPT-4, Gemini & Deepseek")
        
        # Control panel
        with gr.Row():
            with gr.Column(scale=2):
                trading_status = gr.Markdown("**Status:** Ready to trade")
            with gr.Column(scale=1):
                run_trading_btn = gr.Button("▶️ Run Trading Session", variant="primary", size="lg")
            with gr.Column(scale=1):
                auto_refresh_toggle = gr.Checkbox(label="Auto-Refresh (30s)", value=False)
        
        # Trading session handler
        def run_trading_session():
            import asyncio
            from trading_floor import run_trading_session as execute_trading
            
            try:
                yield "**Status:** 🔄 Trading in progress... (~2 min)"
                asyncio.run(execute_trading())
                yield "**Status:** ✅ Complete! Data updated. Refresh to see results."
            except Exception as e:
                yield f"**Status:** ❌ Error: {str(e)}"
        
        run_trading_btn.click(fn=run_trading_session, outputs=trading_status)
        
        # All traders in tabs
        with gr.Tabs():
            trader_components = {}
            
            for trader in traders:
                with gr.Tab(trader.name):
                    portfolio_html = gr.HTML(trader.get_portfolio_value_html())
                    chart = gr.Plot(trader.get_portfolio_chart())
                    logs_html = gr.HTML(trader.get_logs_html())
                    
                    with gr.Row():
                        holdings_table = gr.Dataframe(
                            trader.get_holdings_df(),
                            label="Holdings",
                            interactive=False
                        )
                        transactions_table = gr.Dataframe(
                            trader.get_transactions_df(),
                            label="Recent Trades",
                            interactive=False
                        )
                    
                    refresh_btn = gr.Button("🔄 Refresh Data", size="sm")
                    
                    def refresh_trader(t=trader):
                        t.reload()
                        return [
                            t.get_portfolio_value_html(),
                            t.get_portfolio_chart(),
                            t.get_logs_html(),
                            t.get_holdings_df(),
                            t.get_transactions_df()
                        ]
                    
                    refresh_btn.click(
                       refresh_trader,
                        outputs=[portfolio_html, chart, logs_html, holdings_table, transactions_table]
                    )
                    
                    trader_components[trader.name] = {
                        "portfolio": portfolio_html,
                        "chart": chart,
                        "logs": logs_html,
                        "holdings": holdings_table,
                        "transactions": transactions_table,
                        "trader": trader
                    }
        
        # Auto-refresh logic
        def auto_refresh_all():
            results = []
            for trader_name, components in trader_components.items():
                t = components["trader"]
                t.reload()
                results.extend([
                    t.get_portfolio_value_html(),
                    t.get_portfolio_chart(),
                    t.get_logs_html(),
                    t.get_holdings_df(),
                    t.get_transactions_df()
                ])
            return results
        
        # Timer for auto-refresh
        refresh_timer = gr.Timer(value=30, active=False)
        
        def toggle_auto_refresh(enabled):
            return gr.Timer(active=enabled)
        
        auto_refresh_toggle.change(
            fn=toggle_auto_refresh,
            inputs=auto_refresh_toggle,
            outputs=refresh_timer
        )
        
        all_outputs = []
        for components in trader_components.values():
            all_outputs.extend([
                components["portfolio"],
                components["chart"],
                components["logs"],
                components["holdings"],
                components["transactions"]
            ])
        
        refresh_timer.tick(
            fn=auto_refresh_all,
            outputs=all_outputs,
            show_progress="hidden"
        )
        
        gr.Markdown("""
---
**Strategy Overview:**
- **Warren (GPT-4)**: Value investing → undervalued stocks, dividends
- **George (Gemini)**: Momentum → trending stocks, quick profits  
- **Ray (Deepseek)**: Systematic → technical indicators, rebalancing
- **Cathie (GPT-4)**: Growth & Innovation → disruptive tech, high risk/reward
        """)
    
    return dashboard


if __name__ == "__main__":
    dashboard = create_dashboard()
    dashboard.launch(server_name="0.0.0.0", server_port=7860, share=False)
