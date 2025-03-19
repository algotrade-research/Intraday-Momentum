import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

intraday_data = {}

for i in range(2021, 2025):
    intraday_data[i] = pd.read_csv(f'data/stick_{i}.csv')
    intraday_data[i]['Datetime'] = pd.to_datetime(intraday_data[i]['Datetime'])

class TradingDay:
    def __init__(self, date_data, fee = 0.47):
        self.trading_data = date_data
        self.time_data = date_data['Datetime'].dt.time
        self.fee = fee

    def get_ORB_signal(self, minute_period = 5):
        # Get the candle stick of the first miniute_period given that the trading_data has the time to second
        start_time = pd.to_datetime('09:00:00').time()
        end_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes = minute_period)).time()
        mask = self.time_data.between(start_time, end_time)

        if not mask.any():
            return None, None, None
        
        opening_range = self.trading_data[mask].index
        start_index = opening_range[0]
        end_index = opening_range[-1]
        open_price = self.trading_data['Price'][start_index]
        close_price = self.trading_data['Price'][end_index]

        print(f"Start index: {start_index}, End index: {end_index}")
        return open_price, close_price, end_index
    
    def get_stop_loss(self):
        return 2

    def get_take_profit(self):
        return 2
    
    def ORB_strategy(self):
        open_price, close_price, end_index = self.get_ORB_signal()
        if open_price is None or close_price is None or abs(open_price - close_price) < 0.5:
            return 0
        returns = 0
        holdings = {"signal": None, "entry_point": None}
        stop_loss = self.get_stop_loss()
        take_profit = self.get_take_profit()

        if open_price <= close_price - 0.5:
            holdings['signal'] = 'LONG'
            holdings['entry_point'] = open_price
        elif open_price >= close_price + 0.5:
            holdings['signal'] = 'SHORT'
            holdings['entry_point'] = open_price
        
        
        for index, row in self.trading_data.iterrows():
            if index <= end_index:
                continue
            
            diff = row['Price'] - holdings['entry_point']
            
            if holdings['signal'] == 'LONG':
                if diff > take_profit or diff < -stop_loss:
                    returns = row['Price'] - holdings['entry_point'] - self.fee
                    break
            elif holdings['signal'] == 'SHORT':
                if diff < -take_profit or diff > stop_loss:
                    returns = holdings['entry_point'] - row['Price'] - self.fee
                    break
            
            # If the end of the trading day
            if index == self.trading_data.index[-1]:
                returns = row['Price'] - holdings['entry_point']
        
        print(f"ORB returns: {returns}")
        return returns

def backtesting(data, take_profit, stop_loss, range_time):
    asset = 1000
    returns = []
    cost = 0.47
    
    l = 0
    date_list = data['Datetime'].dt.date
    while (l < len(data)):
        r = l
        # get the date of current datetime
        while (r < len(data) and date_list[r] == date_list[l]):
            r += 1
        print(f"Done {l=}, {r=}")
        trade_day = TradingDay(data[l:r], cost)
        daily_return = trade_day.ORB_strategy()
        asset += daily_return
        returns.append(daily_return)
        l = r
    
    print(f"Total asset: {asset}")
