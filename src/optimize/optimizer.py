import optuna
from optuna.samplers import RandomSampler
import json
import os
from src.backtesting.backtesting import Backtesting

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
            'condition_diff': 0
        }
        max_sharpe_ratio = 0
        backtesting = Backtesting(self.data)
        for i in range(52, 56):
            for j in range(2, 10):
                metric = backtesting.ORB_strategy(period=i, take_profit=2, condition_diff=j)
                if metric.sharpe_ratio() > max_sharpe_ratio:
                    max_sharpe_ratio = metric.sharpe_ratio()
                    optimize_parameters['period'] = i
                    optimize_parameters['condition_diff'] = j
                print(f"period={i}, condition_diff={j}, Sharpe ratio={metric.sharpe_ratio()}")

        print("Finished optimization for ORB strategy")
        print(f"Best hyperparameters: {optimize_parameters}")
        print(f"Best Sharpe ratio: {max_sharpe_ratio}")

    def VWAP_optimize(self):
        optimize_parameters = {
            'period': 0,
            'condition_diff': 0
        }
        max_sharpe_ratio = 0
        backtesting = Backtesting(self.data)
        for i in range(33, 37):
            for j in range(1, 10):
                metric = backtesting.VWAP_strategy(period=i, take_profit=2, condition_diff=j)
                if metric.sharpe_ratio() > max_sharpe_ratio:
                    max_sharpe_ratio = metric.sharpe_ratio()
                    optimize_parameters['period'] = i
                    optimize_parameters['condition_diff'] = j
                print(f"period={i}, diff={j}, Sharpe ratio={metric.sharpe_ratio()}")
        print("Finished optimization for VWAP strategy")
        print(f"Best hyperparameters: {optimize_parameters}")
        print(f"Best Sharpe ratio: {max_sharpe_ratio}")

