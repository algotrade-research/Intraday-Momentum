import psycopg2
from typing import List
from datetime import datetime, time
import pandas as pd

from src.data.query import *
from config.config import *

class DataService:
    def __init__(self):
        self.connection = psycopg2.connect(**db_params)

    def execute_query(self, query, from_date, to_date):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (from_date, to_date))
            result = cursor.fetchall()

            cursor.close()
            return result

        except Exception as e:
            print(f"Error: {e}")


    def get_tick_price(self, year):
        from_date = f"{year}-01-01"
        to_date = f"{year}-12-31"

        columns = ["Datetime", "Price", "Volume"]
        matched = pd.DataFrame(self.execute_query(matched_tick_query, from_date, to_date), columns=columns)
        matched = matched.astype({"Price": float, "Volume": int})

        return matched


    def get_daily(self, year):
        from_date = f"{year}-01-01"
        to_date = f"{year}-12-31"

        columns = ["Datetime", "Open", "Close", "High", "Low"]
        daily = pd.DataFrame(self.execute_query(daily_query, from_date, to_date), columns=columns)
        daily = daily.astype({"Open": float, "Close": float, "High": float, "Low": float})

        return daily

