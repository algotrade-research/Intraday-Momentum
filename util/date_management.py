from datetime import datetime, timedelta

def make_date_to_tickersymbol(date_obj):
    if type(date_obj) is str:
        date_obj = make_date_from_string(date_obj)

    maturity_date = get_maturity_date(date_obj)
    
    year = date_obj.strftime("%y")
    month = date_obj.strftime("%m")

    if date_obj > maturity_date:
        month = str(int(month) + 1)
        # format month is two digit, examples 01, 02, 03 ,04 ,05
        month = month.zfill(2)
        if month == "13":
            month = "01"
            year = str(int(year) + 1)

    return f"VN30F{year}{month}"

def make_date_from_string(input_date):
    if type(input_date) is str:
        try:
            if "," in input_date:
                input_date = input_date.replace(",", ".")
            if "." in input_date:
                date_obj = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S.%f")
            elif ":" in input_date:
                date_obj = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
            else:
                date_obj = datetime.strptime(input_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Please provide a date in the format '%Y-%m-%d' or '%Y-%m-%d %H:%M:%S.%f'. ")
    else:
        date_obj = input_date
    return date_obj

def get_maturity_date(date):
    """Get the third thursday of the month of the given date
    Args:
        date (datetime): _description_

    Returns:
        datetime: _description_
    """
    if type(date) is str:
        date = make_date_from_string(date)
    month = date.strftime("%m")
    year = date.strftime("%y")
    first_day_of_month = datetime.strptime(f"20{year}-{month}-01", "%Y-%m-%d")
    first_thursday = first_day_of_month + timedelta(days=((3-first_day_of_month.weekday()) % 7))
    third_thursday = first_thursday + timedelta(days=14)
    return third_thursday