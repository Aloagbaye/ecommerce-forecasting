"""
Lag feature creation utilities for time series forecasting.
"""

import pandas as pd
import numpy as np
from typing import List, Optional


def create_lag_features(
    df: pd.DataFrame,
    value_col: str = 'units_sold',
    group_col: str = 'sku_id',
    date_col: str = 'date',
    lags: List[int] = [1, 7, 14, 30, 90]
) -> pd.DataFrame:
    """
    Create lag features (historical values) for time series forecasting.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    value_col : str, default 'units_sold'
        Column to create lags for
    group_col : str, default 'sku_id'
        Column to group by (lags computed per group)
    date_col : str, default 'date'
        Date column for sorting
    lags : list of int, default [1, 7, 14, 30, 90]
        Lag periods to create (in days)
        
    Returns
    -------
    pd.DataFrame
        Dataframe with lag features added
        
    Examples
    --------
    >>> df_lags = create_lag_features(df, value_col='units_sold', 
    ...                                group_col='sku_id', lags=[1, 7, 30])
    >>> # Creates: lag_1, lag_7, lag_30
    """
    df = df.copy()
    
    # Ensure date is datetime and sorted
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values([group_col, date_col]).reset_index(drop=True)
    
    # Create lag features per group
    for lag in lags:
        feature_name = f'lag_{lag}'
        df[feature_name] = df.groupby(group_col)[value_col].shift(lag)
    
    return df


def create_lead_features(
    df: pd.DataFrame,
    value_col: str = 'units_sold',
    group_col: str = 'sku_id',
    date_col: str = 'date',
    leads: List[int] = [1, 7, 14]
) -> pd.DataFrame:
    """
    Create lead features (future values) - useful for validation.
    
    Note: Only use for training/validation, not for production forecasting!
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    value_col : str, default 'units_sold'
        Column to create leads for
    group_col : str, default 'sku_id'
        Column to group by
    date_col : str, default 'date'
        Date column for sorting
    leads : list of int, default [1, 7, 14]
        Lead periods to create (in days)
        
    Returns
    -------
    pd.DataFrame
        Dataframe with lead features added
    """
    df = df.copy()
    
    # Ensure date is datetime and sorted
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values([group_col, date_col]).reset_index(drop=True)
    
    # Create lead features per group
    for lead in leads:
        feature_name = f'lead_{lead}'
        df[feature_name] = df.groupby(group_col)[value_col].shift(-lead)
    
    return df

