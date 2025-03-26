import pandas as pd
from datetime import datetime, timedelta
from src.strategy.ORB import Intraday_ORB_strategy
from src.strategy.VWAP import Intraday_VWAP_strategy
from src.metrics.metric import Metric
from src.data.service import DataService

class Backtesting:
    def __init__(self, tick_data):
        self.tick_data = tick_data
        self.length_data = len(tick_data)

    def ORB_strategy(self, period = 5, stop_loss = 2, take_profit = 2):
        asset = 1000
        returns = []
        cost = 0.47
        
        l = 0
        date_list = self.tick_data['Datetime'].dt.date
        while (l < self.length_data):
            r = l
            # get the date of current datetime
            while (r < self.length_data and date_list[r] == date_list[l]):
                r += 1
            trade_day = Intraday_ORB_strategy(period, stop_loss, take_profit)
            for i in range(l, r):
                trade_day.get_tick(self.tick_data['Datetime'][i], self.tick_data['Price'][i])
                if trade_day.get_return() is not None:
                    break
            daily_return = trade_day.get_return()
            asset += daily_return
            returns.append(daily_return)
            l = r
        
        metric = Metric(pd.Series(returns))
        return metric

    def VWAP_strategy(self, period = 5, stop_loss = 2, take_profit = 2):
        asset = 1000
        returns = []
        cost = 0.47

        l = 0
        date_list = self.tick_data['Datetime'].dt.date
        while (l < self.length_data):
            r = l
            # get the date of current datetime
            while (r < self.length_data and date_list[r] == date_list[l]):
                r += 1
            trade_day = Intraday_VWAP_strategy(period, stop_loss, take_profit)
            for i in range(l, r):
                trade_day.get_tick(self.tick_data['Datetime'][i], self.tick_data['Price'][i], self.tick_data['Volume'][i])
                if trade_day.get_return() is not None:
                    break
            daily_return = trade_day.get_return()
            asset += daily_return
            returns.append(daily_return)
            l = r

        metric = Metric(pd.Series(returns))
        return metric
