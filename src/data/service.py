import psycopg2
from typing import List
from datetime import datetime, time
import pandas as pd
import os

from src.data.query import *
from config.config import *

class DataService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.connection = psycopg2.connect(**db_params)
            self.initialized = True

    def create_data_folder(self):
        if not os.path.exists("trading_data"):
            os.makedirs("trading_data")

        for i in range(2021, 2025):
            if not os.path.exists(f"trading_data/{i}_tick.csv"):
                tick = self.__fetch_tick_price(i)
                tick.to_csv(f"trading_data/{i}_tick.csv", index=False)
            if not os.path.exists(f"trading_data/{i}_VNINDEX.csv"):
                vnindex = self.__fetch_vnindex(i)
                vnindex.to_csv(f"trading_data/{i}_VNINDEX.csv", index=False)

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
    
    def __fetch_vnindex(self, year):
        if year != 2021:
            from_date = f"{year}-01-01"
        else:
            from_date = f"{year}-06-01"
        to_date = f"{year}-12-31"

        columns = ["Datetime", "Open", "Close"]
        vnindex = pd.DataFrame(self.__execute_query(VNINDEX_open_close, from_date, to_date), columns=columns)
        vnindex = vnindex.astype({"Open": float, "Close": float})

        return vnindex
    

    def get_tick_price(self, year, quarter = None):
        tick = pd.read_csv(f"trading_data/{year}_tick.csv")
        tick['Datetime'] = pd.to_datetime(tick['Datetime'])
        if quarter:
            tick = tick[tick['Datetime'].dt.quarter == quarter]
        return tick
    
    def get_vnindex(self, year):
        vnindex = pd.read_csv(f"trading_data/{year}_VNINDEX.csv")
        vnindex['Datetime'] = pd.to_datetime(vnindex['Datetime'])
        return vnindex
