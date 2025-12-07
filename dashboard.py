"""Gradio dashboard for AI trading simulation"""
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
            return go.Figure()
        
        df = pd.DataFrame(
            self.account.portfolio_value_time_series,
            columns=["datetime", "value"]
        )
        df["datetime"] = pd.to_datetime(df["datetime"])
        
        fig = px.line(df, x="datetime", y="value", title=f"{self.name}'s Portfolio")
        fig.update_layout(
            height=300,
            margin=dict(l=40, r=20, t=40, b=40),
            xaxis_title=None,
            yaxis_title="Value ($)",
            paper_bgcolor="#1a1a1a",
            plot_bgcolor="#2d2d2d",
            font=dict(color="white")
        )
        fig.update_xaxes(tickformat="%m/%d %H:%M", tickangle=45)
        fig.update_yaxes(tickformat="$,.0f")
        return fig
    
    def get_portfolio_value_html(self):
        """Get portfolio value with P&L"""
        portfolio_value = self.account.calculate_portfolio_value()
        pnl = self.account.calculate_profit_loss(portfolio_value)
        
        color = "green" if pnl >= 0 else "red"
        emoji = "⬆" if pnl >= 0 else "⬇"
        
        return f"""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;'>
            <h2 style='color: white; margin: 0;'>{self.name}</h2>
            <p style='color: #ccc; margin: 5px 0;'>{self.model_name}</p>
            <h1 style='color: white; margin: 10px 0;'>${portfolio_value:,.2f}</h1>
            <p style='color: {color}; font-size: 24px; margin: 0;'>{emoji} ${abs(pnl):,.2f} ({(pnl/10000)*100:+.1f}%)</p>
        </div>
        """
    
    def get_holdings_df(self):
        """Get holdings as DataFrame"""
        if not self.account.holdings:
            return pd.DataFrame(columns=["Symbol", "Quantity"])
        
        return pd.DataFrame([
            {"Symbol": symbol, "Quantity": qty}
            for symbol, qty in self.account.holdings.items()
        ])
    
    def get_transactions_df(self):
        """Get recent transactions"""
        transactions = self.account.list_transactions()
        if not transactions:
            return pd.DataFrame(columns=["Time", "Symbol", "Qty", "Price", "Rationale"])
        
        # Show last 10
        recent = transactions[-10:]
        return pd.DataFrame([{
            "Time": t["timestamp"].split()[1] if " " in t["timestamp"] else t["timestamp"],
            "Symbol": t["symbol"],
            "Qty": t["quantity"],
            "Price": f"${t['price']:.2f}",
            "Rationale": t["rationale"][:50] + "..." if len(t["rationale"]) > 50 else t["rationale"]
        } for t in recent])
    
    def get_logs_html(self):
        """Get colored activity logs"""
        logs = read_log(self.name, last_n=15)
        
        colors = {
            "agent": "#00bcd4",
            "function": "#4caf50",
            "response": "#ff4081",
            "account": "#f44336",
            "error": "#ff5722"
        }
        
        html = "<div style='height: 200px; overflow-y: auto; background: #1a1a1a; padding: 10px; border-radius: 5px;'>"
        for timestamp, log_type, message in logs:
            color = colors.get(log_type, "#ffffff")
            html += f"<p style='color: {color}; margin: 3px 0; font-size: 12px;'>{timestamp} [{log_type}] {message}</p>"
        html += "</div>"
        return html


def create_dashboard():
    """Create the Gradio dashboard"""
    
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
        .markdown h1, .markdown h2, .markdown h3 {color: white !important;}
        .markdown p {color: #cccccc !important;}
        """
    ) as dashboard:
        
        gr.Markdown(
            """
            # 🏦 AI Trading Simulation Dashboard
            ### Real-time monitoring of 4 AI traders with different strategies
            """,
            elem_classes=["markdown"]
        )
        
        # Create tabs for each trader
        with gr.Tabs():
            for trader in traders:
                with gr.Tab(trader.name):
                    with gr.Row():
                        portfolio_html = gr.HTML(trader.get_portfolio_value_html())
                    
                    with gr.Row():
                        chart = gr.Plot(trader.get_portfolio_chart())
                    
                    with gr.Row():
                        logs_html = gr.HTML(trader.get_logs_html())
                    
                    with gr.Row():
                        with gr.Column():
                            holdings_table = gr.Dataframe(
                                trader.get_holdings_df(),
                                label="Current Holdings",
                                interactive=False
                            )
                        
                        with gr.Column():
                            transactions_table = gr.Dataframe(
                                trader.get_transactions_df(),
                                label="Recent Transactions",
                                interactive=False
                            )
                    
                    # Auto-refresh every 30 seconds
                    def refresh_trader(trader=trader):
                        trader.reload()
                        return [
                            trader.get_portfolio_value_html(),
                            trader.get_portfolio_chart(),
                            trader.get_logs_html(),
                            trader.get_holdings_df(),
                            trader.get_transactions_df()
                        ]
                    
                    refresh_btn = gr.Button("🔄 Refresh", size="sm")
                    refresh_btn.click(
                        refresh_trader,
                        outputs=[portfolio_html, chart, logs_html, holdings_table, transactions_table]
                    )
        
        gr.Markdown(
            """
            ---
            **Strategy Overview:**
            - **Warren (GPT-4)**: Value investing, long-term holds
            - **George (Gemini)**: Momentum trading, quick profits
            - **Ray (Deepseek)**: Systematic quantitative approach
            - **Cathie (GPT-4)**: Growth & innovation focus
            """
        )
    
    return dashboard


if __name__ == "__main__":
    dashboard = create_dashboard()
    dashboard.launch(server_name="0.0.0.0", server_port=7860, share=False)
