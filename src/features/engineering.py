"""
Feature engineering functions for e-commerce forecasting.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Union


def create_temporal_features(
    df: pd.DataFrame,
    date_col: str = 'date'
) -> pd.DataFrame:
    """
    Create temporal features from date column.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with date column
    date_col : str, default 'date'
        Name of the date column
        
    Returns
    -------
    pd.DataFrame
        Dataframe with temporal features added
        
    Features Created:
    - year, month, day, day_of_week, day_of_month
    - week, quarter
    - is_weekend, is_month_start, is_month_end
    - day_of_week_sin, day_of_week_cos (cyclical)
    - month_sin, month_cos (cyclical)
    """
    df = df.copy()
    
    if date_col not in df.columns:
        raise ValueError(f"Date column '{date_col}' not found in dataframe")
    
    # Ensure date is datetime
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Basic temporal features
    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month
    df['day'] = df[date_col].dt.day
    df['day_of_week'] = df[date_col].dt.dayofweek  # 0=Monday, 6=Sunday
    df['day_of_month'] = df[date_col].dt.day
    df['week'] = df[date_col].dt.isocalendar().week
    df['quarter'] = df[date_col].dt.quarter
    
    # Binary flags
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['is_month_start'] = (df['day'] <= 3).astype(int)
    df['is_month_end'] = (df['day'] >= 28).astype(int)
    
    # Holiday season (October-December)
    df['is_holiday_season'] = df['month'].isin([10, 11, 12]).astype(int)
    
    # Cyclical encoding for day of week (preserves cyclical nature)
    df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    # Cyclical encoding for month (preserves cyclical nature)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    return df


def create_rolling_features(
    df: pd.DataFrame,
    value_col: str = 'units_sold',
    group_col: str = 'sku_id',
    date_col: str = 'date',
    windows: List[int] = [7, 14, 30, 90],
    functions: List[str] = ['mean', 'std', 'min', 'max', 'median']
) -> pd.DataFrame:
    """
    Create rolling window statistics.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    value_col : str, default 'units_sold'
        Column to compute rolling statistics on
    group_col : str, default 'sku_id'
        Column to group by (typically SKU)
    date_col : str, default 'date'
        Date column for sorting
    windows : list of int, default [7, 14, 30, 90]
        Window sizes in days
    functions : list of str, default ['mean', 'std', 'min', 'max', 'median']
        Functions to compute
        
    Returns
    -------
    pd.DataFrame
        Dataframe with rolling features added
    """
    df = df.copy()
    
    # Ensure date is datetime and sorted
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values([group_col, date_col]).reset_index(drop=True)
    
    # Create rolling features per group
    for window in windows:
        for func in functions:
            feature_name = f'rolling_{func}_{window}'
            
            if func == 'mean':
                df[feature_name] = df.groupby(group_col)[value_col].transform(
                    lambda x: x.rolling(window=window, min_periods=1).mean()
                )
            elif func == 'std':
                df[feature_name] = df.groupby(group_col)[value_col].transform(
                    lambda x: x.rolling(window=window, min_periods=1).std()
                )
            elif func == 'min':
                df[feature_name] = df.groupby(group_col)[value_col].transform(
                    lambda x: x.rolling(window=window, min_periods=1).min()
                )
            elif func == 'max':
                df[feature_name] = df.groupby(group_col)[value_col].transform(
                    lambda x: x.rolling(window=window, min_periods=1).max()
                )
            elif func == 'median':
                df[feature_name] = df.groupby(group_col)[value_col].transform(
                    lambda x: x.rolling(window=window, min_periods=1).median()
                )
    
    return df


def create_promotion_features(
    df: pd.DataFrame,
    promo_col: str = 'promotion_flag',
    group_col: str = 'sku_id',
    date_col: str = 'date',
    windows: List[int] = [7, 14, 30]
) -> pd.DataFrame:
    """
    Create promotion-related features.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    promo_col : str, default 'promotion_flag'
        Promotion flag column
    group_col : str, default 'sku_id'
        Column to group by
    date_col : str, default 'date'
        Date column for sorting
    windows : list of int, default [7, 14, 30]
        Time windows for promotion history
        
    Returns
    -------
    pd.DataFrame
        Dataframe with promotion features added
    """
    df = df.copy()
    
    if promo_col not in df.columns:
        return df  # Return unchanged if no promotion column
    
    # Ensure date is datetime and sorted
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values([group_col, date_col]).reset_index(drop=True)
    
    # Convert promotion flag to numeric if boolean
    if df[promo_col].dtype == bool:
        df[promo_col] = df[promo_col].astype(int)
    
    # Promotion count in last N days
    for window in windows:
        feature_name = f'promo_last_{window}_days'
        df[feature_name] = df.groupby(group_col)[promo_col].transform(
            lambda x: x.rolling(window=window, min_periods=1).sum()
        )
    
    # Days since last promotion — vectorized: forward-fill the most recent promo date per SKU
    df['_promo_date'] = df[date_col].where(df[promo_col] > 0, other=pd.NaT)
    df['_promo_date'] = df.groupby(group_col)['_promo_date'].ffill()
    df['days_since_last_promo'] = (df[date_col] - df['_promo_date']).dt.days.fillna(999)
    df = df.drop(columns=['_promo_date'])
    
    return df


def create_price_features(
    df: pd.DataFrame,
    price_col: str = 'price',
    group_col: str = 'sku_id',
    date_col: str = 'date',
    windows: List[int] = [7, 30]
) -> pd.DataFrame:
    """
    Create price-related features.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    price_col : str, default 'price'
        Price column
    group_col : str, default 'sku_id'
        Column to group by
    date_col : str, default 'date'
        Date column for sorting
    windows : list of int, default [7, 30]
        Time windows for price statistics
        
    Returns
    -------
    pd.DataFrame
        Dataframe with price features added
    """
    df = df.copy()
    
    if price_col not in df.columns:
        return df  # Return unchanged if no price column
    
    # Ensure date is datetime and sorted
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values([group_col, date_col]).reset_index(drop=True)
    
    # Price change percentage
    df['price_lag_1'] = df.groupby(group_col)[price_col].shift(1)
    df['price_change_pct'] = ((df[price_col] - df['price_lag_1']) / df['price_lag_1'] * 100).fillna(0)
    
    # Rolling price statistics
    for window in windows:
        # Rolling mean
        df[f'price_rolling_mean_{window}'] = df.groupby(group_col)[price_col].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean()
        )
        
        # Price relative to rolling average
        df[f'price_relative_to_avg_{window}'] = df[price_col] / (df[f'price_rolling_mean_{window}'] + 1e-6)
    
    # Price volatility (rolling std)
    df['price_rolling_std_7'] = df.groupby(group_col)[price_col].transform(
        lambda x: x.rolling(window=7, min_periods=1).std()
    )
    
    return df


def create_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create interaction features.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with base features
        
    Returns
    -------
    pd.DataFrame
        Dataframe with interaction features added
    """
    df = df.copy()
    
    # Month × Day of week interaction
    if 'month' in df.columns and 'day_of_week' in df.columns:
        df['month_day_interaction'] = df['month'] * df['day_of_week']
    
    # Holiday season × Weekend
    if 'is_holiday_season' in df.columns and 'is_weekend' in df.columns:
        df['holiday_weekend'] = df['is_holiday_season'] * df['is_weekend']
    
    # Promotion × Weekend
    if 'promotion_flag' in df.columns and 'is_weekend' in df.columns:
        promo_numeric = df['promotion_flag']
        if promo_numeric.dtype == bool:
            promo_numeric = promo_numeric.astype(int)
        df['promo_weekend'] = promo_numeric * df['is_weekend']
    
    # Peak period (November-December weekends)
    if 'month' in df.columns and 'is_weekend' in df.columns:
        df['is_peak_period'] = (df['month'].isin([11, 12]) & (df['is_weekend'] == 1)).astype(int)
    
    # Quarter × Day of week
    if 'quarter' in df.columns and 'day_of_week' in df.columns:
        df['quarter_day_interaction'] = df['quarter'] * df['day_of_week']
    
    return df

