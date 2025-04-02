import argparse
from src.backtesting.backtesting import *
from src.data.service import *
from src.metrics.metric import *
from src.metrics.util import *
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run backtesting with strategy')
    parser.add_argument('-m', '--mode', type=int, help='Which data to run backtesting with, in-sample or out-of-sample.', required=True)
    parser.add_argument('-s', '--strategy', type=str, help='Strategy to run backtesting with.', required=True)
    parser.add_argument('-p', '--parameter', type=int, help='Initial parameter or Optimized parameter', required=True)

    args = parser.parse_args()
    data_service = DataService()
    if args.mode == 0:
        # In-sample data
        in_sample_data_2021 = DataService().get_tick_price(2021)
        in_sample_data_2022 = DataService().get_tick_price(2022)
        in_sample_benchmark_2021 = DataService().get_vnindex(2021)
        in_sample_benchmark_2022 = DataService().get_vnindex(2022)
        in_sample_benchmark = pd.concat([in_sample_benchmark_2021, in_sample_benchmark_2022], ignore_index=True)
        in_sample_data = pd.concat([in_sample_data_2021, in_sample_data_2022], ignore_index=True)
        tick_data = in_sample_data
        benchmark_data = in_sample_benchmark
    else:
        # Out-of-sample data
        out_of_sample_data_2023 = DataService().get_tick_price(2023)
        out_of_sample_data_2024 = DataService().get_tick_price(2024)
        out_of_sample_data = pd.concat([out_of_sample_data_2023, out_of_sample_data_2024], ignore_index=True)
        out_of_sample_benchmark_2023 = DataService().get_vnindex(2023)
        out_of_sample_benchmark_2024 = DataService().get_vnindex(2024)
        out_of_sample_benchmark = pd.concat([out_of_sample_benchmark_2023, out_of_sample_benchmark_2024], ignore_index=True)
        tick_data = out_of_sample_data
        benchmark_data = out_of_sample_benchmark

    backtesting = Backtesting(tick_data)

    backtesting_benchmark = Backtesting(benchmark_data)
    benchmark_metric = Metric(pd.Series(backtesting_benchmark.VNINDEX_benchmark()), is_benchmark=True)
    
    print('Benchmark metric:')
    benchmark_metric.print_metrics()
    print('--------------------------------')
    if args.strategy == 'ORB':
        if args.parameter == 0:
            pnl_per_trade, date_per_trade = backtesting.ORB_strategy(30, 2, 1)
            metric = Metric(pd.Series(pnl_per_trade), benchmark_metric, is_benchmark=False)
        elif args.parameter == 1:
            pnl_per_trade, date_per_trade = backtesting.ORB_strategy(33, 2, 5)
            metric = Metric(pd.Series(pnl_per_trade), benchmark_metric, is_benchmark=False)
        print('ORB strategy:')
        metric.print_metrics()
        metric.plot_asset_value(save_path='img/ORB_asset_value.png')
        results = calculate_returns_by_period(pnl_per_trade, date_per_trade)
        print(results['yearly'])
        print(results['monthly'])
    
    if args.strategy == 'VWAP':
        if args.parameter == 0:
            pnl_per_trade, date_per_trade = backtesting.VWAP_strategy(30, 2, 1)
            metric = Metric(pd.Series(pnl_per_trade), benchmark_metric, is_benchmark=False)
        elif args.parameter == 1:
            pnl_per_trade, date_per_trade = backtesting.VWAP_strategy(33, 2, 3)
            metric = Metric(pd.Series(pnl_per_trade), benchmark_metric, is_benchmark=False)
        print('VWAP strategy:')
        metric.print_metrics()
        metric.plot_asset_value(save_path='img/VWAP_asset_value.png')
        results = calculate_returns_by_period(pnl_per_trade, date_per_trade)
        print(results['yearly'])
        print(results['monthly'])
    
