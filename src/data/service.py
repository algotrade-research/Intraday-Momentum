import psycopg2
from typing import List
from datetime import datetime, time
import pandas as pd
import os

from src.data.query import *
from config.config import *

class DataService:
    def __init__(self):
        self.connection = psycopg2.connect(**db_params)

    def create_data_folder(self):
        if not os.path.exists("trading_data"):
            os.makedirs("trading_data")

        for i in range(2021, 2025):
            tick = self.__fetch_tick_price(i)

            tick.to_csv(f"trading_data/{i}_tick.csv", index=False)

    def __execute_query(self, query, from_date, to_date):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (from_date, to_date))
            result = cursor.fetchall()

            cursor.close()
            return result

        except Exception as e:
            print(f"Error: {e}")


    def __fetch_tick_price(self, year):
        from_date = f"{year}-01-01"
        to_date = f"{year}-12-31"

        columns = ["Datetime", "Price", "Volume"]
        matched = pd.DataFrame(self.__execute_query(matched_tick_query, from_date, to_date), columns=columns)
        matched = matched.astype({"Price": float, "Volume": int})

        return matched

    def get_tick_price(self, year):
        tick = pd.read_csv(f"trading_data/{year}_tick.csv")
        tick['Datetime'] = pd.to_datetime(tick['Datetime'])
        return tick

    # def get_daily(self, year):
    #     from_date = f"{year}-01-01"
    #     to_date = f"{year}-12-31"

    #     columns = ["Datetime", "Open", "Close", "High", "Low"]
    #     daily = pd.DataFrame(self.execute_query(daily_query, from_date, to_date), columns=columns)
    #     daily = daily.astype({"Open": float, "Close": float, "High": float, "Low": float})

    #     return daily

