import logging
import json
import redis
import pytz
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
from config.config import redis_host, redis_port, redis_password
from src.strategy.ORB import Intraday_ORB_strategy
from util.date_management import *
from src.metrics.metric import Metric

class Pipeline():
    def __init__(self):
        self.logger = None
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
        self.redis_client.ping()
        self.cur_date = None
        self.time_zone = pytz.timezone('Asia/Ho_Chi_Minh')
        self.strategy = None
        self.initial_asset = 1000
        self.returns = []
        self.return_dates = []
        self.folder_path = 'papertrade_results'
        self.ORB_path = os.path.join(self.folder_path, 'ORB_strategy')
        self.finish_trade = False

    
    def _init_logging(self, log_file = 'log.log', name='logger'):
        """
        Initialize logger
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        logger.handlers.clear()
        logger.addHandler(file_handler)

        return logger
    
    def _log_results(self):
        metric = Metric(pd.Series(self.returns))
        self.logger.info("Results")
        self.logger.info(f"Sharpe ratio: {metric.sharpe_ratio()}")
        self.logger.info(f"Sortino ratio: {metric.sortino_ratio()}")
        self.logger.info(f"Profit: {metric.final_pnl()}")
        self.logger.info(f"Maximum drawdown: {metric.maximum_drawdown()}")
    
    def _plot_results(self, directory):
        """
        Plot the assets by adding the returns and save the plot
        """
        plt.plot(self.return_dates, np.cumsum(self.returns))
        plt.xlabel('Date')
        plt.ylabel('Return')
        plt.title('Return over time with ORB strategy')
        filename = os.path.join(directory, 'asset.png')
        plt.savefig(filename)

    def _create_directory(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        if not os.path.exists(self.ORB_path):
            os.makedirs(self.ORB_path)

    def _export_results(self, directory):
        """
        Export the results to a csv file
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        df = pd.DataFrame({
            'Date': self.return_dates,
            'Return': self.returns
        })
        filename = os.path.join(directory, 'results.csv')
        df.to_csv(filename, index=False)
        self.logger.info(f"Results exported to {filename}")

    def ORB_papertrade(self):
        """
        Run papertrade for ORB strategy
        """
        def message_handler(message):
            """
            Handle message from redis
            """
            quote = json.loads(message['data'])
            cur_price = quote['latest_matched_price']
            cur_volume = quote['latest_matched_quantity']
            now = datetime.fromtimestamp(quote['timestamp'], self.time_zone)

            if cur_price is None:
                return
            
            self.logger.info(f'{now} - Price: {cur_price} - Volume: {cur_volume}')
            
            if self.cur_date is None or self.cur_date != now.date():
                self.cur_date = now.date()
                self.strategy = Intraday_ORB_strategy(period=30, stop_loss=2, take_profit=2)
                self.finish_trade = False
            
            self.strategy.get_tick(now, cur_price)

            if self.strategy.get_return() is not None and not self.finish_trade:
                self.finish_trade = True
                self.logger.info(f'{now} - Return: {self.strategy.get_return()}')
                self.returns.append(self.strategy.get_return())
                self.return_dates.append(now.date())
                self.asset += self.strategy.get_return()
                self.logger.info(f'{now} - Asset: {self.asset}')
                self.plot_results(self.ORB_path)
                return

        self._create_directory()
        self.logger = self._init_logging(log_file=os.path.join(self.ORB_path, 'log.log'))
        self.logger.info("Starting papertrade")
        ticker_symbol = get_current_tickersymbol()
        F1M_CHANNEL = f'HNXDS:{ticker_symbol}'
        print(f"Listening to channel {F1M_CHANNEL}")
        pub_sub = self.redis_client.pubsub()
        pub_sub.psubscribe(**{F1M_CHANNEL: message_handler})    
        pubsub_thread = pub_sub.run_in_thread(sleep_time=1)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self._log_results()
            pubsub_thread.stop()