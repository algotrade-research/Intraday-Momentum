import optuna
from optuna.samplers import RandomSampler
import json

from src.metrics.metric import Metric
from src.data.service import DataService
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
    
    def ORB_optimize(self): 
        def objective(trial):
            # Suggest values for the hyperparameters
            period = trial.suggest_int('period', self.ranges['ORB']['period'][0], self.ranges['ORB']['period'][1])
            stop_loss = trial.suggest_int('stop_loss', self.ranges['ORB']['stop_loss'][0], self.ranges['ORB']['stop_loss'][1])
            take_profit = trial.suggest_int('take_profit', self.ranges['ORB']['take_profit'][0], self.ranges['ORB']['take_profit'][1])
            
            # Run the ORB strategy with the suggested hyperparameters
            backtesting = Backtesting(self.data)
            metric = backtesting.ORB_strategy(period=period, stop_loss=stop_loss, take_profit=take_profit)
            
            # Return the negative Sharpe ratio (since Optuna minimizes the objective function)
            return -metric.sharpe_ratio()
        
        # Create a study object and optimize the objective function
        study = optuna.create_study(sampler=RandomSampler(seed=self.seed), direction='minimize')
        study.optimize(objective, n_trials=self.trials)
        
        # Print the best hyperparameters
        print("Finished optimization for ORB strategy")
        print(f"Best hyperparameters: {study.best_params}")
        print(f"Best Sharpe ratio: {-study.best_value}")

        # Save the best hyperparameters into a json file
        with open('orb_best_hyperparameters.json', 'w') as f:
            json.dump(study.best_params, f, indent=4)

    def VWAP_optimize(self):
        def objective(trial):
            # Suggest values for the hyperparameters
            period = trial.suggest_int('period', self.ranges['VWAP']['period'][0], self.ranges['VWAP']['period'][1])
            stop_loss = trial.suggest_int('stop_loss', self.ranges['VWAP']['stop_loss'][0], self.ranges['VWAP']['stop_loss'][1])
            take_profit = trial.suggest_int('take_profit', self.ranges['VWAP']['take_profit'][0], self.ranges['VWAP']['take_profit'][1])
            
            # Run the VWAP strategy with the suggested hyperparameters
            backtesting = Backtesting(self.data)
            metric = backtesting.VWAP_strategy(period=period, stop_loss=stop_loss, take_profit=take_profit)
            
            # Return the negative Sharpe ratio (since Optuna minimizes the objective function)
            return -metric.sharpe_ratio()
        
        # Create a study object and optimize the objective function
        study = optuna.create_study(sampler=RandomSampler(seed=self.seed), direction='minimize')
        study.optimize(objective, n_trials=self.trials)
        
        # Print the best hyperparameters
        print("Finished optimization for VWAP strategy")
        print(f"Best hyperparameters: {study.best_params}")
        print(f"Best Sharpe ratio: {-study.best_value}")

        # Save the best hyperparameters into a json file
        with open('vwap_best_hyperparameters.json', 'w') as f:
            json.dump(study.best_params, f, indent=4)