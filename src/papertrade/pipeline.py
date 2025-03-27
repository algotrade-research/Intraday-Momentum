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
from metrics.metric import Metric

class Pipeline():
    def __init__(self):
        self.logger = None
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
        self.redis_client.ping()
        self.logger = self._init_logging()
        self.cur_date = None
        self.time_zone = pytz.timezone('Asia/Ho_Chi_Minh')
        self.strategy = None
        self.initial_asset = 1000
        self.returns = []
        self.return_dates = []
        self.folder_path = 'papertrade_results'
        self.ORB_path = os.path.join(self.folder_path, 'ORB_strategy')


    
    def _init_logging(self, log_file = 'log.txt', name='logger'):
        """
        Initialize logger
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.handlers.clear()
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        return logger
    
    def _log_results(self):
        metric = Metric(pd.Series(self.returns))
        self.logger.info("Results")
        self.logger.info(f"Sharpe ratio: {metric.sharpe_ratio()}")
        self.logger.info(f"Sortino ratio: {metric.sortino_ratio()}")
        self.logger.info(f"Profit: {metric.final_pnl()}")
        self.logger.info(f"Maximum drawdown: {metric.maximum_drawdown()}")
    
    def plot_results(self, directory):
        """
        Plot the assets by adding the returns and save the plot
        """
        plt.plot(self.return_dates, np.cumsum(self.returns) + self.initial_asset)
        plt.xlabel('Date')
        plt.ylabel('Asset')
        plt.title('Asset over time with ORB strategy')
        filename = os.path.join(directory, 'asset.png')
        plt.savefig(filename)

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
            
            if self.cur_date is None or self.cur_date != now.date():
                self.cur_date = now.date()
                self.strategy = Intraday_ORB_strategy(period=30, stop_loss=2, take_profit=2)
            
            self.strategy.get_tick(now, cur_price)

            if self.strategy.get_return() is not None:
                self.logger.info(f'{now} - Return: {self.strategy.get_return()}')
                self.returns.append(self.strategy.get_return())
                self.return_dates.append(now.date())
                self.asset += self.strategy.get_return()
                self.logger.info(f'{now} - Asset: {self.asset}')
                self.plot_results(self.ORB_path)
                return

    
        current_date = datetime.now().astimezone(self.time_zone)
        ticker_symbol = make_date_to_tickersymbol(current_date)
        F1M_CHANNEL = f'HNXDS:{ticker_symbol}'
        pub_sub = self.redis_client.pubsub()
        pub_sub.psubscribe(**{F1M_CHANNEL: message_handler})    
        pubsub_thread = pub_sub.run_in_thread(sleep_time=1)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self._log_results()
            pubsub_thread.stop()