import optuna
from optuna.samplers import RandomSampler
import json
import os
from src.backtesting.backtesting import Backtesting
from src.metrics.metric import Metric
import pandas as pd

class Optimizer:
    def __init__(self, data):
        self.data = data
        self.ranges = {
            'ORB': {
                'period': (1, 150),
                'stop_loss': (2, 10),
                'take_profit': (2, 10)
            },
            'VWAP': {
                'period': (1, 150),
                'stop_loss': (2, 10),
                'take_profit': (2, 10)
            }
        }
        self.trials = 20
        self.seed = 42
        self.folder = 'optimize'
        self._create_folder()

    def _create_folder(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
    
    def ORB_optimize(self): 
        optimize_parameters = {
            'period': 0,
            'condition_diff': 0, 
            'take_profit': 0
        }
        max_sharpe_ratio = 0
        backtesting = Backtesting(self.data)
        for i in range(5, 150, 5):
            pnl_per_trade, date_per_trade = backtesting.ORB_strategy(period=i, take_profit=2, condition_diff=1)
            metric = Metric(pd.Series(pnl_per_trade), None, is_benchmark=True)
            if metric.sharpe_ratio() > max_sharpe_ratio:
                max_sharpe_ratio = metric.sharpe_ratio()
                optimize_parameters['period'] = i
                optimize_parameters['condition_diff'] = 1
                print(f"period={i}, condition_diff=1, Sharpe ratio={metric.sharpe_ratio()}")

        for i in range(optimize_parameters['period'] - 5, optimize_parameters['period'] + 5):
            for j in range(1, 10):
                pnl_per_trade, date_per_trade = backtesting.ORB_strategy(period=i, take_profit=2, condition_diff=j)
                metric = Metric(pd.Series(pnl_per_trade), None, is_benchmark=True)
                if metric.sharpe_ratio() > max_sharpe_ratio:
                    max_sharpe_ratio = metric.sharpe_ratio()
                    optimize_parameters['period'] = i
                    optimize_parameters['condition_diff'] = j
                print(f"period={i}, condition_diff={j}, Sharpe ratio={metric.sharpe_ratio()}")

        for i in range(1, 4):  
            pnl_per_trade, date_per_trade = backtesting.ORB_strategy(period=optimize_parameters['period'], take_profit=i, condition_diff=optimize_parameters['condition_diff'])
            metric = Metric(pd.Series(pnl_per_trade), None, is_benchmark=True)
            if metric.sharpe_ratio() > max_sharpe_ratio:
                max_sharpe_ratio = metric.sharpe_ratio()
                optimize_parameters['take_profit'] = i
            print(f"period={optimize_parameters['period']}, condition_diff={optimize_parameters['condition_diff']}, take_profit={i}, Sharpe ratio={metric.sharpe_ratio()}")

        print("Finished optimization for ORB strategy")
        print(f"Best hyperparameters: {optimize_parameters}")
        print(f"Best Sharpe ratio: {max_sharpe_ratio}")
        with open('optimize\ORB_optimize_result.json', 'w') as f:
            json.dump(optimize_parameters, f)

    def VWAP_optimize(self):
        optimize_parameters = {
            'period': 0,
            'condition_diff': 0,
            'take_profit': 0
        }
        max_sharpe_ratio = 0
        backtesting = Backtesting(self.data)
        for i in range(5, 150, 5):
            pnl_per_trade, date_per_trade = backtesting.VWAP_strategy(period=i, take_profit=2, condition_diff=1)
            metric = Metric(pd.Series(pnl_per_trade), None, is_benchmark=True)
            if metric.sharpe_ratio() > max_sharpe_ratio:
                max_sharpe_ratio = metric.sharpe_ratio()
                optimize_parameters['period'] = i
                optimize_parameters['condition_diff'] = 1
            print(f"period={i}, condition_diff=1, Sharpe ratio={metric.sharpe_ratio()}")

        for i in range(optimize_parameters['period'] - 5, optimize_parameters['period'] + 5):
            for j in range(1, 10):
                pnl_per_trade, date_per_trade = backtesting.VWAP_strategy(period=i, take_profit=2, condition_diff=j)
                metric = Metric(pd.Series(pnl_per_trade), None, is_benchmark=True)
                if metric.sharpe_ratio() > max_sharpe_ratio:
                    max_sharpe_ratio = metric.sharpe_ratio()
                    optimize_parameters['period'] = i
                    optimize_parameters['condition_diff'] = j
                print(f"period={i}, diff={j}, Sharpe ratio={metric.sharpe_ratio()}")

        for i in range(1, 4):
            pnl_per_trade, date_per_trade = backtesting.VWAP_strategy(period=optimize_parameters['period'], take_profit=i, condition_diff=optimize_parameters['condition_diff'])
            metric = Metric(pd.Series(pnl_per_trade), None, is_benchmark=True)
            if metric.sharpe_ratio() > max_sharpe_ratio:
                max_sharpe_ratio = metric.sharpe_ratio()
                optimize_parameters['take_profit'] = i
            print(f"period={optimize_parameters['period']}, condition_diff={optimize_parameters['condition_diff']}, take_profit={i}, Sharpe ratio={metric.sharpe_ratio()}")


        print("Finished optimization for VWAP strategy")
        print(f"Best hyperparameters: {optimize_parameters}")
        print(f"Best Sharpe ratio: {max_sharpe_ratio}")
        with open('optimize\VWAP_optimize_result.json', 'w') as f:
            json.dump(optimize_parameters, f)
