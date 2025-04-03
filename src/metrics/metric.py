import numpy as np
import matplotlib.pyplot as plt
from math import sqrt

class Metric: 
    def __init__(self, pnl_per_trade, benchmark_metric=None, is_benchmark=False):
        self.pnl_per_trade = pnl_per_trade
        self.num_trades = len(pnl_per_trade)
        self.std_dev_pnl = pnl_per_trade.std()
        self.mean_pnl = pnl_per_trade.mean()
        self.period = 252
        self.annual_risk_free_rate = 0.03  # 3% annually
        self.daily_risk_free_rate = self.annual_risk_free_rate / self.period  # Daily rate
        self.initial_capital = 500
        self.is_benchmark = is_benchmark
        self.benchmark_metric = benchmark_metric

    def sharpe_ratio(self):
        """
        Calculate Sharpe ratio using percentage returns derived from absolute PnL values.
        """
        # Convert absolute PnL to percentage returns
        percentage_returns = self.pnl_per_trade / self.initial_capital
        
        # Calculate mean and std dev of percentage returns
        mean_return = np.mean(percentage_returns)
        std_dev_return = np.std(percentage_returns)
        
        # Calculate Sharpe ratio
        return sqrt(self.period) * (mean_return - self.daily_risk_free_rate) / std_dev_return
    
    def sortino_ratio(self):
        """
        Calculate Sortino ratio using percentage returns derived from absolute PnL values.
        """
        # Convert absolute PnL to percentage returns
        percentage_returns = self.pnl_per_trade / self.initial_capital
        
        # Calculate downside deviation (only negative returns)
        downside_returns = percentage_returns[percentage_returns < 0]
        if len(downside_returns) == 0:
            return float('inf')  # No downside risk
        
        downside_std_dev = np.std(downside_returns)
        
        # Calculate Sortino ratio
        mean_return = np.mean(percentage_returns)
        return sqrt(self.period) * (mean_return - self.daily_risk_free_rate) / downside_std_dev
    
    def holding_period_return(self):
        return self.final_pnl() / self.initial_capital
    
    def excess_holding_period_return(self):
        """
        Calculate excess holding period return over the risk-free rate.
        """
        # Get total holding period return
        holding_return = self.holding_period_return()
        
        if self.is_benchmark:
            return None
        else:
            return holding_return - self.benchmark_metric.holding_period_return()
    
    def annualized_return(self):
        """
        Calculate annualized return based on actual asset amounts.
        Converts absolute PnL values to percentage returns first, then annualizes.
        """
        # Calculate cumulative PnL
        cumulative_pnl = np.sum(self.pnl_per_trade)
        
        # Convert to actual return percentage
        total_return = cumulative_pnl / self.initial_capital
        
        # Annualize the return
        years = self.num_trades / 250
        
        # Calculate annualized return
        annualized = (1 + total_return) ** (1 / years) - 1
        
        return annualized

    def win_rate(self):
        return len(self.pnl_per_trade[self.pnl_per_trade > 0]) / self.num_trades
    
    def maximum_drawdown(self):
        cum_pnl = np.cumsum(self.pnl_per_trade) + np.ones(self.num_trades) * self.initial_capital
        running_max = np.maximum.accumulate(cum_pnl)
        drawdown = running_max - cum_pnl
        drawdown_pct = drawdown / running_max
        max_drawdown_pct = np.max(drawdown_pct)
        return max_drawdown_pct * 100

    def final_pnl(self):
        return np.sum(self.pnl_per_trade)
    
    def final_excess_return(self):
        if self.is_benchmark:
            return None
        else:
            return (self.final_pnl() - self.benchmark_metric.final_pnl()) / self.initial_capital
    
    def print_metrics(self):
        if not self.is_benchmark:
            print(f"Holding period return: {self.holding_period_return() * 100}%")
            print(f"Excess holding period return: {self.excess_holding_period_return() * 100}%")
            print(f"Annualized return: {self.annualized_return() * 100}%")
            print(f"Annualized excess return: {self.annualized_excess_return() * 100}%")
            print(f"Maximum drawdown: {self.maximum_drawdown()}%")
            print(f"Longest drawdown: {self.longest_drawdown()}")
            print(f"Turnover ratio: {self.turnover_ratio()}")
            print(f"Sharpe ratio: {self.sharpe_ratio()}")
            print(f"Sortino ratio: {self.sortino_ratio()}")
            print(f"Information ratio: {self.information_ratio()}")
            print(f"Final PnL: {self.final_pnl()}")
            print(f"Final excess return: {self.final_excess_return() * 100}%")
        else:
            print(f"Holding period return: {self.holding_period_return() * 100}%")
            print(f"Annualized return: {self.annualized_return() * 100}%")
            print(f"Maximum drawdown: {self.maximum_drawdown()}%")
            print(f"Longest drawdown: {self.longest_drawdown()}")
            print(f"Sharpe ratio: {self.sharpe_ratio()}")
            print(f"Sortino ratio: {self.sortino_ratio()}")
    
    def plot_pnl(self):
        plt.plot(np.cumsum(self.pnl_per_trade))
        plt.xlabel('Trade')
        plt.ylabel('Cumulative PnL')
        plt.title('Cumulative PnL')
        plt.show()

    def annualized_excess_return(self):
        """
        Calculate annualized excess return over risk-free rate based on actual asset amounts.
        """
        # Calculate annualized return first
        annualized = self.annualized_return()
        
        if self.is_benchmark:
            return None
        else:
            return annualized - self.benchmark_metric.annualized_return()

    def longest_drawdown(self):
        cum_pnl = np.cumsum(self.pnl_per_trade) + np.ones(self.num_trades) * self.initial_capital
        running_max = np.maximum.accumulate(cum_pnl)
        drawdown = running_max - cum_pnl
        
        # Initialize variables for tracking drawdown periods
        current_drawdown_length = 0
        max_drawdown_length = 0
        in_drawdown = False
        
        for dd in drawdown:
            if dd > 0:  # We're in a drawdown
                if not in_drawdown:  # Start of new drawdown
                    in_drawdown = True
                current_drawdown_length += 1
            else:  # No drawdown
                if in_drawdown:  # End of drawdown
                    max_drawdown_length = max(max_drawdown_length, current_drawdown_length)
                    current_drawdown_length = 0
                    in_drawdown = False
        
        # Check if we're still in drawdown at the end
        if in_drawdown:
            max_drawdown_length = max(max_drawdown_length, current_drawdown_length)
        
        return max_drawdown_length

    def turnover_ratio(self):
        """
        Calculate the turnover ratio which measures trading activity relative to the capital.
        Turnover Ratio = Total Trading Volume / Average Capital
        
        Assumes position size of 1 unit per trade, regardless of PnL.
        """
        # With consistent position size of 1 per trade
        total_volume = self.num_trades  # Each trade involves 1 unit
        
        # Calculate average capital over the period
        cum_pnl = np.cumsum(self.pnl_per_trade) + np.ones(self.num_trades) * self.initial_capital
        average_capital = np.mean(cum_pnl)
        
        # Calculate turnover ratio
        turnover = total_volume / average_capital
        
        return turnover

    def plot_asset_value(self, save_path='asset_value_plot.png'):
        """
        Plot the asset value (cumulative PnL + initial capital) over time and save it to a file.
        
        Parameters:
        -----------
        save_path : str
            The file path where the plot will be saved
        """
        # Calculate cumulative asset value
        cum_pnl = np.cumsum(self.pnl_per_trade)
        asset_value = cum_pnl + self.initial_capital
        
        # Create x-axis (trade numbers)
        trades = np.arange(1, self.num_trades + 1)
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(trades, asset_value, 'b-', linewidth=2)
        plt.axhline(y=self.initial_capital, color='r', linestyle='--', label='Initial Capital')
        
        # Add labels and title
        plt.xlabel('Trade Number')
        plt.ylabel('Asset Value')
        plt.title('Asset Value Over Time')
        plt.grid(True)
        plt.legend()
        
        # No annotation
        
        plt.tight_layout()
        
        # Save the figure
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()  # Close the figure to free memory
        
        print(f"Plot saved to {save_path}")

    def information_ratio(self):
        """
        Calculate Information Ratio with percentage returns.
        """
        # Convert absolute PnL to percentage returns
        percentage_returns = self.pnl_per_trade / self.initial_capital
        benchmark_returns = self.benchmark_metric.pnl_per_trade / self.benchmark_metric.initial_capital

        excess_returns = percentage_returns - benchmark_returns

        # Calculate tracking error
        tracking_error = np.std(percentage_returns - benchmark_returns)
        
        # Calculate Information Ratio
        ir = (np.mean(excess_returns) / tracking_error) * sqrt(self.period)
        
        return ir