import numpy as np
import pandas as pd
from datetime import datetime

def calculate_period_return(pnl_per_trade, date_per_trade, period='yearly'):
    """
    Calculate returns aggregated by specified time periods (yearly, quarterly, monthly, weekly).
    
    Parameters:
    -----------
    pnl_per_trade : array-like
        The profit and loss values for each trade
    date_per_trade : array-like
        The dates corresponding to each trade (datetime objects or strings in format 'YYYY-MM-DD')
    period : str
        The aggregation period - 'yearly', 'quarterly', 'monthly', or 'weekly'
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with columns: 'period', 'return', 'num_trades'
    """
    # Convert to pandas Series for easier manipulation
    if not isinstance(date_per_trade[0], datetime):
        # Convert string dates to datetime if needed
        dates = pd.to_datetime(date_per_trade)
    else:
        dates = date_per_trade
        
    # Create DataFrame with dates and PnL
    df = pd.DataFrame({
        'date': dates,
        'pnl': pnl_per_trade
    })
    
    # Add period columns
    df['year'] = df['date'].dt.year
    df['quarter'] = df['date'].dt.quarter
    df['month'] = df['date'].dt.month
    df['week'] = df['date'].dt.isocalendar().week
    
    # Define grouping based on period
    if period.lower() == 'yearly':
        grouped = df.groupby('year')
        period_col = 'year'
    elif period.lower() == 'quarterly':
        df['year_quarter'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
        grouped = df.groupby('year_quarter')
        period_col = 'year_quarter'
    elif period.lower() == 'monthly':
        df['year_month'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)
        grouped = df.groupby('year_month')
        period_col = 'year_month'
    elif period.lower() == 'weekly':
        df['year_week'] = df['year'].astype(str) + '-W' + df['week'].astype(str).str.zfill(2)
        grouped = df.groupby('year_week')
        period_col = 'year_week'
    else:
        raise ValueError("Period must be 'yearly', 'quarterly', 'monthly', or 'weekly'")
    
    # Calculate aggregate returns for each period
    results = []
    for period_name, group in grouped:
        period_return = np.sum(group['pnl'])
        num_trades = len(group)
        results.append({
            'period': period_name,
            'return': period_return,
            'num_trades': num_trades
        })
    
    # Convert results to DataFrame
    result_df = pd.DataFrame(results)
    
    # Sort by period
    result_df = result_df.sort_values('period')
    
    return result_df

def calculate_returns_by_period(pnl_per_trade, date_per_trade, initial_capital=None):
    """
    Calculate returns for multiple time periods at once.
    
    Parameters:
    -----------
    pnl_per_trade : array-like
        The profit and loss values for each trade
    date_per_trade : array-like
        The dates corresponding to each trade
    initial_capital : float, optional
        Initial capital to convert absolute returns to percentages
        
    Returns:
    --------
    dict
        Dictionary with different period DataFrames: 'yearly', 'quarterly', 'monthly', 'weekly'
    """
    periods = ['yearly', 'quarterly', 'monthly', 'weekly']
    results = {}
    
    for period in periods:
        period_df = calculate_period_return(pnl_per_trade, date_per_trade, period)
        
        # Add percentage return if initial capital is provided
        if initial_capital is not None:
            period_df['return_pct'] = period_df['return'] / initial_capital * 100
            
        results[period] = period_df
    
    return results
    
