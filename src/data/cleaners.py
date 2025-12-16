"""
Data cleaning utilities for e-commerce sales data.
"""

import pandas as pd
import numpy as np
from typing import Optional, Union, List
from pathlib import Path


def fill_missing_dates(
    df: pd.DataFrame,
    date_col: str = 'date',
    group_col: str = 'sku_id',
    fill_value: Union[int, float, str] = 0,
    fill_col: Optional[str] = None
) -> pd.DataFrame:
    """
    Fill missing dates for each group (e.g., SKU) in the dataset.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with date column
    date_col : str, default 'date'
        Name of the date column
    group_col : str, default 'sku_id'
        Column to group by (typically SKU)
    fill_value : int, float, or str, default 0
        Value to fill for missing dates
    fill_col : str, optional
        Column to fill with fill_value. If None, fills all numeric columns with 0.
        
    Returns
    -------
    pd.DataFrame
        Dataframe with missing dates filled
        
    Examples
    --------
    >>> df_clean = fill_missing_dates(df, date_col='date', group_col='sku_id')
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Get date range
    min_date = df[date_col].min()
    max_date = df[date_col].max()
    all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
    
    # Create complete date-SKU combinations
    all_groups = df[group_col].unique()
    
    # Create MultiIndex with all combinations
    complete_index = pd.MultiIndex.from_product(
        [all_groups, all_dates],
        names=[group_col, date_col]
    )
    
    # Set index
    df_indexed = df.set_index([group_col, date_col])
    
    # Reindex to include all dates
    df_complete = df_indexed.reindex(complete_index)
    
    # Fill missing values
    if fill_col:
        df_complete[fill_col] = df_complete[fill_col].fillna(fill_value)
    else:
        # Fill numeric columns with fill_value, others with forward fill
        numeric_cols = df_complete.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df_complete[col] = df_complete[col].fillna(fill_value)
        
        # Forward fill non-numeric columns (like category, sku_id)
        non_numeric_cols = df_complete.select_dtypes(exclude=[np.number]).columns
        for col in non_numeric_cols:
            df_complete[col] = df_complete.groupby(level=0)[col].fillna(method='ffill')
    
    # Reset index
    df_complete = df_complete.reset_index()
    
    return df_complete


def handle_outliers(
    df: pd.DataFrame,
    column: str,
    method: str = 'cap',
    lower_percentile: float = 0.01,
    upper_percentile: float = 0.99,
    group_col: Optional[str] = None
) -> pd.DataFrame:
    """
    Handle outliers in a column.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    column : str
        Column to handle outliers for
    method : str, default 'cap'
        Method to handle outliers: 'cap' (limit values) or 'remove' (drop rows)
    lower_percentile : float, default 0.01
        Lower percentile for outlier detection
    upper_percentile : float, default 0.99
        Upper percentile for outlier detection
    group_col : str, optional
        If provided, compute percentiles per group (e.g., per SKU)
        
    Returns
    -------
    pd.DataFrame
        Dataframe with outliers handled
        
    Examples
    --------
    >>> df_clean = handle_outliers(df, column='units_sold', method='cap')
    >>> df_clean = handle_outliers(df, column='units_sold', method='cap', group_col='sku_id')
    """
    df = df.copy()
    
    if group_col:
        # Compute percentiles per group
        def cap_outliers_group(group):
            lower_bound = group[column].quantile(lower_percentile)
            upper_bound = group[column].quantile(upper_percentile)
            
            if method == 'cap':
                group[column] = group[column].clip(lower=lower_bound, upper=upper_bound)
            elif method == 'remove':
                group = group[(group[column] >= lower_bound) & (group[column] <= upper_bound)]
            
            return group
        
        df = df.groupby(group_col).apply(cap_outliers_group).reset_index(drop=True)
    else:
        # Compute percentiles globally
        lower_bound = df[column].quantile(lower_percentile)
        upper_bound = df[column].quantile(upper_percentile)
        
        if method == 'cap':
            df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
        elif method == 'remove':
            df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    
    return df


def remove_duplicates(
    df: pd.DataFrame,
    subset: Optional[List[str]] = None,
    keep: str = 'first'
) -> pd.DataFrame:
    """
    Remove duplicate records.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    subset : list of str, optional
        Columns to check for duplicates. If None, checks all columns.
    keep : str, default 'first'
        Which duplicates to keep: 'first', 'last', or False (drop all)
        
    Returns
    -------
    pd.DataFrame
        Dataframe with duplicates removed
    """
    return df.drop_duplicates(subset=subset, keep=keep)


def validate_cleaned_data(df: pd.DataFrame) -> dict:
    """
    Validate cleaned data quality.
    
    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataframe to validate
        
    Returns
    -------
    dict
        Validation results
    """
    issues = []
    recommendations = []
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        high_missing = missing[missing > len(df) * 0.1]
        if len(high_missing) > 0:
            issues.append(f"High missing values in: {high_missing.to_dict()}")
            recommendations.append("Consider imputation or removal of high-missing columns")
    
    # Check for infinite values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    inf_count = (df[numeric_cols] == np.inf).sum().sum()
    if inf_count > 0:
        issues.append(f"Infinite values found: {inf_count}")
        recommendations.append("Replace infinite values with NaN or large finite values")
    
    # Check for negative sales (if units_sold exists)
    if 'units_sold' in df.columns:
        negative_sales = (df['units_sold'] < 0).sum()
        if negative_sales > 0:
            issues.append(f"Negative sales values: {negative_sales}")
            recommendations.append("Investigate negative sales (returns?)")
    
    # Check date continuity
    if 'date' in df.columns and 'sku_id' in df.columns:
        date_gaps = df.groupby('sku_id')['date'].apply(
            lambda x: (x.max() - x.min()).days - len(x) + 1
        )
        large_gaps = date_gaps[date_gaps > len(df) * 0.1]
        if len(large_gaps) > 0:
            issues.append(f"Large date gaps in {len(large_gaps)} SKUs")
            recommendations.append("Consider filling missing dates")
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues,
        'recommendations': recommendations,
        'shape': df.shape,
        'missing_values': missing.to_dict() if 'missing' in locals() else {}
    }

