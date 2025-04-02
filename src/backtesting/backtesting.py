import pandas as pd
from datetime import datetime, timedelta
from src.strategy.ORB import Intraday_ORB_strategy
from src.strategy.VWAP import Intraday_VWAP_strategy
from src.strategy.Market_Timing import Market_Timing
from src.metrics.metric import Metric
from src.data.service import DataService

class Backtesting:
    def __init__(self, data):
        self.data = data
        self.length_data = len(data)

    def ORB_strategy(self, period = 5, take_profit = 2, condition_diff = 2):
        pnl_per_trade = []
        date_per_trade = []
        
        l = 0
        date_list = self.data['Datetime'].dt.date
        while (l < self.length_data):
            r = l
            # get the date of current datetime
            while (r < self.length_data and date_list[r] == date_list[l]):
                r += 1
            trade_day = Intraday_ORB_strategy(period, take_profit, condition_diff)
            for i in range(l, r):
                trade_day.get_tick(self.data['Datetime'][i], self.data['Price'][i])
                if trade_day.get_return() is not None:
                    break
            daily_return = trade_day.get_return()
            pnl_per_trade.append(daily_return)
            date_per_trade.append(self.data['Datetime'][l].date())
            l = r
        
        return pnl_per_trade, date_per_trade

    def VWAP_strategy(self, period = 5, take_profit = 2, condition_diff = 0):
        pnl_per_trade = []
        date_per_trade = []

        l = 0
        date_list = self.data['Datetime'].dt.date
        while (l < self.length_data):
            r = l
            # get the date of current datetime
            while (r < self.length_data and date_list[r] == date_list[l]):
                r += 1
            trade_day = Intraday_VWAP_strategy(period, take_profit, condition_diff)
            for i in range(l, r):
                trade_day.get_tick(self.data['Datetime'][i], self.data['Price'][i], self.data['Volume'][i])
                if trade_day.get_return() is not None:
                    break
            daily_return = trade_day.get_return()
            pnl_per_trade.append(daily_return)
            date_per_trade.append(self.data['Datetime'][l].date())
            l = r

        return pnl_per_trade, date_per_trade
    
    def Market_Timing_strategy(self, period = 5, take_profit = 2, condition_diff = 2):
        pnl_per_trade = []
        date_per_trade = []
        
        l = 0
        date_list = self.data['Datetime'].dt.date
        while (l < self.length_data):
            r = l
            # get the date of current datetime
            while (r < self.length_data and date_list[r] == date_list[l]):
                r += 1
            trade_day = Market_Timing(period, take_profit, condition_diff)
            for i in range(l, r):
                trade_day.get_tick(self.data['Datetime'][i], self.data['Price'][i])
                if trade_day.get_return() is not None:
                    break
            daily_return = trade_day.get_return()
            pnl_per_trade.append(daily_return)
            date_per_trade.append(self.data['Datetime'][l].date())
            l = r
        
        return pnl_per_trade, date_per_trade
    
    def VNINDEX_benchmark(self):
        pnl_per_trade = []
        for i in range(self.length_data - 1):
            pnl_per_trade.append(self.data['Close'][i+1] - self.data['Close'][i])
        
        return pnl_per_trade
