import argparse
from src.backtesting.backtesting import *
from src.data.service import *
from src.metrics.metric import *
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run backtesting with selected year, strategy and period.')
    parser.add_argument('-y', '--year', type=int, help='Year to run backtesting with.', required=True)
    parser.add_argument('-s', '--strategy', type=str, help='Strategy to run backtesting with.', required=True)

    args = parser.parse_args()
    data_service = DataService()
    tick_data = data_service.get_tick_price(args.year)
    backtesting = Backtesting(tick_data)
    
    if args.strategy == 'ORB':
        # Load the best hyperparameters from the json file
        with open('orb_best_hyperparameters.json', 'r') as f:
            best_hyperparameters = json.load(f)
        metric = backtesting.ORB_strategy(5, 2, 2)
        metric.print_metrics()
    
    if args.strategy == 'VWAP':
        with open('vwap_best_hyperparameters.json', 'r') as f:
            best_hyperparameters = json.load(f)
        metric = backtesting.VWAP_strategy(best_hyperparameters['period'], best_hyperparameters['stop_loss'], best_hyperparameters['take_profit'])
        print('VWAP strategy:')
        metric.print_metrics()
    