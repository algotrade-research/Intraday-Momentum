import numpy as np
import matplotlib.pyplot as plt

class Metric: 
    def __init__(self, pnl_per_trade):
        self.pnl_per_trade = pnl_per_trade
        self.num_trades = len(pnl_per_trade)
        self.std_dev_pnl = pnl_per_trade.std()
        self.mean_pnl = pnl_per_trade.mean()
        self.risk_fee_rate = 0.06
        self.period = 252
    
    def sharpe_ratio(self):
        """
        Calculate the Sharpe ratio of the trading strategy
        """
        return (self.mean_pnl - self.risk_fee_rate) / self.std_dev_pnl
    
    def sortino_ratio(self):
        downside_returns = self.pnl_per_trade[self.pnl_per_trade < 0]
        downside_std_dev = downside_returns.std()
        return (self.mean_pnl - self.risk_fee_rate) / downside_std_dev
    
    def win_rate(self):
        return len(self.pnl_per_trade[self.pnl_per_trade > 0]) / self.num_trades
    
    def maximum_drawdown(self):
        cum_pnl = np.cumsum(self.pnl_per_trade) + np.ones(self.num_trades) * 1000
        running_max = np.maximum.accumulate(cum_pnl)
        drawdown = running_max - cum_pnl
        drawdown_pct = drawdown / running_max
        max_drawdown_pct = np.max(drawdown_pct)
        return max_drawdown_pct * 100
    
    def plot_pnl(self):
        plt.plot(np.cumsum(self.pnl_per_trade))
        plt.xlabel('Trade')
        plt.ylabel('Cumulative PnL')
        plt.title('Cumulative PnL')
        plt.show()