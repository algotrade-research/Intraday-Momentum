import pandas as pd
from datetime import datetime, timedelta

class Intraday_VWAP_strategy:
    def __init__(self, period):
        self.fee = 0.47
        self.intraday_data = pd.DataFrame(columns=['Datetime', 'Price'])
        self.time_point = {
            'start_range': pd.to_datetime('09:00:00').time(),
            'end_range': (datetime.combine(datetime.today(), pd.to_datetime('09:00:00').time()) + timedelta(minutes = period)).time(),
            'end_day': pd.to_datetime('14:29:00').time(),
        }
        self.holding = {"signal": None, "entry_point": None}
        self.accumulate_price = 0
        self.accumulate_volume = 0
        self.daily_return = None
        self.stop_loss = 2
        self.take_profit = 2

    def get_signal(self, price):
        if self.accumulate_volume == 0:
            return None
        
        vwap = self.accumulate_price / self.accumulate_volume
        
        if price > vwap:
            return 'LONG'

        if price < vwap:
            return 'SHORT'
    
    def get_return(self):
        return self.daily_return
    
    def handle_timestamp(self, datetime):
        if datetime.time() < self.time_point['start_range']:
            return 'PREPARE'
        elif datetime.time() <= self.time_point['end_range']:
            return 'COLLECT'
        elif datetime.time() < self.time_point['end_day']:
            return 'TRADE'
        else:
            return 'END'
        
    def collect_data(self, price, volume):
        self.accumulate_price += price * volume
        self.accumulate_volume += volume

    def trade(self, price):
        if self.daily_return is not None:
            return
        
        if self.holding['signal'] is None:
            signal = self.get_signal(price)
            if signal is not None:
                self.holding['signal'] = signal
                self.holding['entry_point'] = price
                return 
            else:
                self.daily_return = 0
                return
        else:
            diff = price - self.holding['entry_point']
            if self.holding['signal'] == 'LONG':
                if diff > self.take_profit or diff < -self.stop_loss:
                    self.daily_return = diff - self.fee
                    return
            elif self.holding['signal'] == 'SHORT':
                if diff < -self.take_profit or diff > self.stop_loss:
                    self.daily_return = -diff - self.fee
                    return
    
    def end_of_day(self, price):
        if self.daily_return is not None:
            return
        
        if self.holding['signal'] is not None:
            diff = price - self.holding['entry_point']
            if self.holding['signal'] == 'LONG':
                self.daily_return = diff - self.fee
            elif self.holding['signal'] == 'SHORT':
                self.daily_return = -diff - self.fee



    def get_tick(self, datetime, price, volume):
        if self.daily_return is not None:
            return
        
        time_status = self.handle_timestamp(datetime)

        if time_status == 'PREPARE':
            return
        elif time_status == 'COLLECT':
            self.collect_data(price, volume)
            return 
        elif time_status == 'TRADE':
            self.trade(price)
            return 
        elif time_status == 'END':
            self.end_of_day(price)
            return