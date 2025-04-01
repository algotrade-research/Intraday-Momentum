from src.optimize.optimizer import Optimizer
from src.data.service import DataService
import argparse
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run backtesting with selected strategy')
    parser.add_argument('-s', '--strategy', type=str, help='Strategy to run backtesting with.', required=True)
    args = parser.parse_args()
    in_sample_data_2021 = DataService().get_tick_price(2021)
    in_sample_data_2022 = DataService().get_tick_price(2022)
    in_sample_data = pd.concat([in_sample_data_2021, in_sample_data_2022], ignore_index=True)
    optimizer = Optimizer(in_sample_data)
    if args.strategy == 'ORB':
        optimizer.ORB_optimize()
    elif args.strategy == 'VWAP':
        optimizer.VWAP_optimize()