from datetime import datetime, timedelta

def get_current_tickersymbol():
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    if day > 15:
        month += 1
        if month > 12:
            month = 1
            year += 1
    if month < 10:
        month = f"0{month}"
    else:
        month = str(month)
    year = str(year)[-2:]
    return f"VN30F{year}{month}"