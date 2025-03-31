import pandas as pd
from datetime import datetime, timedelta

class Market_Timing:
    def __init__(self, period, take_profit = 2, condition_diff = 2):
        self.fee = 0.47
        self.intraday_data = pd.DataFrame(columns=['Datetime', 'Price'])
        self.time_point = {
            'start_range': pd.to_datetime('09:00:00').time(),
            'end_range': (datetime.combine(datetime.today(), pd.to_datetime('09:00:00').time()) + timedelta(minutes = period)).time(),
            'end_morning_session': pd.to_datetime('11:30:00').time(),
            'start_trading_session': pd.to_datetime('14:00:00').time(),
            'end_day': pd.to_datetime('14:29:00').time(),
        }
        self.holding = {"signal": None, "entry_point": None}
        self.first_candle_prices = {"open": None, "close": None, "high": None, "low": None}
        self.daily_return = None
        self.stop_loss_price = None
        self.take_profit = take_profit
        self.condition_diff = condition_diff

    def get_signal(self):
        if self.first_candle_prices['open'] is None \
            or self.first_candle_prices['close'] is None \
            or abs(self.first_candle_prices['open'] - self.first_candle_prices['close']) <= self.condition_diff:
            return None
        
        if self.first_candle_prices['open'] < self.first_candle_prices['close']:
            self.stop_loss_price = self.first_candle_prices['low']
            return 'LONG'

        if self.first_candle_prices['open'] > self.first_candle_prices['close']:
            self.stop_loss_price = self.first_candle_prices['high']
            return 'SHORT'
        
    def get_stop_loss_signal(self, price):
        if self.holding['signal'] == 'LONG':
            if price < self.stop_loss_price - self.condition_diff:
                return True
        elif self.holding['signal'] == 'SHORT':
            if price > self.stop_loss_price + self.condition_diff:
                return True
        return False
    
    def get_return(self):
        return self.daily_return
    
    def handle_timestamp(self, datetime):
        if datetime.time() < self.time_point['start_range']:
            return 'PREPARE'
        elif datetime.time() <= self.time_point['end_range']:
            return 'COLLECT'
        elif datetime.time() < self.time_point['end_morning_session']:
            return 'PREPARE'
        elif datetime.time() < self.time_point['start_trading_session']:
            return 'PREPARE'
        elif datetime.time() < self.time_point['end_day']:
            return 'TRADE'
        else:
            return 'END'
        
    def collect_data(self, price):
        if self.first_candle_prices['open'] is None:
            self.first_candle_prices['open'] = price
        self.first_candle_prices['close'] = price
        if self.first_candle_prices['high'] is None or price > self.first_candle_prices['high']:
            self.first_candle_prices['high'] = price
        if self.first_candle_prices['low'] is None or price < self.first_candle_prices['low']:
            self.first_candle_prices['low'] = price
    
    def trade(self, price):
        if self.daily_return is not None:
            return
        
        if self.holding['signal'] is None:
            signal = self.get_signal()
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
                if diff > self.take_profit or self.get_stop_loss_signal(price):
                    self.daily_return = diff - self.fee
                    return
            elif self.holding['signal'] == 'SHORT':
                if diff < -self.take_profit or self.get_stop_loss_signal(price):
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



    def get_tick(self, datetime, price):
        if self.daily_return is not None:
            return
        
        time_status = self.handle_timestamp(datetime)

        if time_status == 'PREPARE':
            return
        elif time_status == 'COLLECT':
            self.collect_data(price)
            return 
        elif time_status == 'TRADE':
            self.trade(price)
            return 
        elif time_status == 'END':
            self.end_of_day(price)
            return