import argparse
from src.backtesting.backtesting import *
from src.data.service import *
from src.metrics.metric import *
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run backtesting with strategy')
    parser.add_argument('-m', '--mode', type=int, help='Which data to run backtesting with, in-sample or out-of-sample.', required=True)
    parser.add_argument('-s', '--strategy', type=str, help='Strategy to run backtesting with.', required=True)

    args = parser.parse_args()
    data_service = DataService()
    if args.mode == 0:
        # In-sample data
        in_sample_data_2021 = DataService().get_tick_price(2021)
        in_sample_data_2022 = DataService().get_tick_price(2022)
        in_sample_data_2023_1 = DataService().get_tick_price(2023, 1)
        in_sample_data_2023_2 = DataService().get_tick_price(2023, 2)
        in_sample_data = pd.concat([in_sample_data_2021, in_sample_data_2022, in_sample_data_2023_1, in_sample_data_2023_2], ignore_index=True)
        tick_data = in_sample_data
    else:
        # Out-of-sample data
        out_of_sample_data_2023_3 = DataService().get_tick_price(2023, 3)
        out_of_sample_data_2023_4 = DataService().get_tick_price(2023, 4)
        out_of_sample_data_2024 = DataService().get_tick_price(2024)
        out_of_sample_data = pd.concat([out_of_sample_data_2023_3, out_of_sample_data_2023_4, out_of_sample_data_2024], ignore_index=True)
        tick_data = out_of_sample_data

    backtesting = Backtesting(tick_data)
    
    if args.strategy == 'ORB':
        # Load the best hyperparameters from the json file
        with open('orb_best_hyperparameters.json', 'r') as f:
            best_hyperparameters = json.load(f)
        metric = backtesting.ORB_strategy(33, 2, 5)
        metric.print_metrics()
    
    if args.strategy == 'VWAP':
        metric = backtesting.VWAP_strategy(33, 2, 2)
        print('VWAP strategy:')
        metric.print_metrics()

    if args.strategy == 'Market_Timing':
        metric = backtesting.Market_Timing_strategy(30, 2, 0)
        print('Market Timing strategy:')
        metric.print_metrics()
    