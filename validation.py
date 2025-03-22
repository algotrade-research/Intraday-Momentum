from src.backtesting.backtesting import *
from src.data.service import *

if __name__ == "__main__":
    data_service = DataService()
    tick_2021 = data_service.get_tick_price(2021)
    backtesting = Backtesting(tick_2021)
    backtesting.ORB_strategy()
    