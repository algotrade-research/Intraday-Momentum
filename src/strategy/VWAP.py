import pandas as pd
from datetime import datetime, timedelta

class Intraday_VWAP_strategy:
    def __init__(self, period, take_profit = 2):
        self.fee = 0.47
        self.intraday_data = pd.DataFrame(columns=['Datetime', 'Price'])
        self.time_point = {
            'start_range': pd.to_datetime('09:00:00').time(),
            'end_range': (datetime.combine(datetime.today(), pd.to_datetime('09:00:00').time()) + timedelta(minutes = period)).time(),
            'end_morning_session': pd.to_datetime('11:30:00').time(),
            'start_afternoon_session': pd.to_datetime('13:00:00').time(),
            'end_day': pd.to_datetime('14:29:00').time(),
        }
        self.holding = {"signal": None, "entry_point": None}
        self.previous_candle = {
            'open': 0, 
            'close': 0, 
            'minute': None
        }
        self.current_candle = {
            'open': 0,
            'close': 0,
            'minute': None
        }
        self.current_minute = None
        self.accumulate_price = 0
        self.accumulate_volume = 0
        self.vwap = 0
        self.daily_return = None
        self.take_profit = take_profit

    def get_entry_signal(self):
        if self.accumulate_volume == 0:
            return None
        
        if self.previous_candle['close'] > self.vwap + 0.5:
            return 'LONG'

        if self.previous_candle['close'] < self.vwap - 0.5:
            return 'SHORT'
        
    def get_stop_loss_signal(self):
        if self.holding['signal'] == 'LONG':
            if self.previous_candle['close'] < self.vwap:
                return True
        elif self.holding['signal'] == 'SHORT':
            if self.previous_candle['close'] > self.vwap:
                return True
        return False
    
    def update_candlestick(self, datetime, price, volume):
        current_minute = datetime.replace(second=0, microsecond=0)
        self.accumulate_price += price * volume
        self.accumulate_volume += volume
        self.vwap = self.accumulate_price / self.accumulate_volume

        if self.current_minute != current_minute:
            self.previous_candle = self.current_candle.copy()
            self.current_candle = {
                'open': price,
                'close': price,
                'minute': current_minute
            }
        else:
            self.current_candle['close'] = price

    def get_return(self):
        return self.daily_return
    
    def handle_timestamp(self, datetime):
        if datetime.time() < self.time_point['end_range']:
            return 'PREPARE'
        elif datetime.time() < self.time_point['end_morning_session']:
            return 'TRADE'
        elif datetime.time() < self.time_point['start_afternoon_session']:
            return 'PREPARE'
        elif datetime.time() < self.time_point['end_day']:
            return 'TRADE'
        else:
            return 'END'

    def trade(self, price):    
        if self.holding['signal'] is None:
            signal = self.get_entry_signal()
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
                if diff > self.take_profit or self.get_stop_loss_signal():
                    self.daily_return = diff - self.fee
                    return
            elif self.holding['signal'] == 'SHORT':
                if diff < -self.take_profit or self.get_stop_loss_signal():
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
        
        self.update_candlestick(datetime, price, volume)
        
        time_status = self.handle_timestamp(datetime)

        if time_status == 'PREPARE':
            return
        elif time_status == 'TRADE':
            self.trade(price)
            return 
        elif time_status == 'END':
            self.end_of_day(price)
            return