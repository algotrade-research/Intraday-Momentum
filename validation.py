import argparse
from src.backtesting.backtesting import *
from src.data.service import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run backtesting with selected year, strategy and period.')
    parser.add_argument('-y', '--year', type=int, help='Year to run backtesting with.', required=True)
    parser.add_argument('-s', '--strategy', type=str, help='Strategy to run backtesting with.', required=True)
    parser.add_argument('-p', '--period', type=int, help='Period to run backtesting with.', required=True)

    args = parser.parse_args()
    data_service = DataService()
    tick_data = data_service.get_tick_price(args.year)
    backtesting = Backtesting(tick_data)
    
    if args.strategy == 'ORB':
        backtesting.ORB_strategy(args.period)
    
    if args.strategy == 'VWAP':
        backtesting.VWAP_strategy(args.period)
    