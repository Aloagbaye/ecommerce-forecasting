"""
Data loading utilities for e-commerce sales data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Union


def load_sales_data(
    file_path: Union[str, Path],
    date_column: str = 'date',
    parse_dates: bool = True
) -> pd.DataFrame:
    """
    Load e-commerce sales data from CSV file.
    
    Parameters
    ----------
    file_path : str or Path
        Path to the CSV file
    date_column : str, default 'date'
        Name of the date column
    parse_dates : bool, default True
        Whether to parse the date column as datetime
        
    Returns
    -------
    pd.DataFrame
        Loaded sales data with date column parsed
        
    Examples
    --------
    >>> df = load_sales_data('data/raw/sales.csv')
    >>> df.head()
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    # Load data
    df = pd.read_csv(file_path)
    
    # Parse dates if requested
    if parse_dates and date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values([date_column, 'sku_id']).reset_index(drop=True)
    
    return df


def load_sample_data() -> pd.DataFrame:
    """
    Load the sample generated data if it exists.
    
    Returns
    -------
    pd.DataFrame
        Sample sales data
        
    Raises
    ------
    FileNotFoundError
        If sample data file doesn't exist
    """
    sample_path = Path('data/raw/sample_sales.csv')
    
    if not sample_path.exists():
        raise FileNotFoundError(
            "Sample data not found. Run: python scripts/generate_sample_data.py"
        )
    
    return load_sales_data(sample_path)


def validate_data(df: pd.DataFrame) -> dict:
    """
    Validate e-commerce sales data structure and quality.
    
    Parameters
    ----------
    df : pd.DataFrame
        Sales data to validate
        
    Returns
    -------
    dict
        Validation results with issues and recommendations
    """
    issues = []
    recommendations = []
    
    # Required columns
    required_columns = ['date', 'sku_id', 'units_sold']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        issues.append(f"Missing required columns: {missing_columns}")
        recommendations.append("Ensure data contains: date, sku_id, units_sold")
    
    # Check for missing values
    if 'date' in df.columns:
        missing_dates = df['date'].isna().sum()
        if missing_dates > 0:
            issues.append(f"Missing dates: {missing_dates} rows")
            recommendations.append("Handle missing dates before modeling")
    
    if 'units_sold' in df.columns:
        missing_sales = df['units_sold'].isna().sum()
        if missing_sales > 0:
            issues.append(f"Missing sales values: {missing_sales} rows")
            recommendations.append("Impute or remove rows with missing sales")
        
        # Check for negative sales
        negative_sales = (df['units_sold'] < 0).sum()
        if negative_sales > 0:
            issues.append(f"Negative sales values: {negative_sales} rows")
            recommendations.append("Investigate and handle negative sales (returns?)")
    
    # Check date range
    if 'date' in df.columns and df['date'].dtype == 'datetime64[ns]':
        date_range = df['date'].max() - df['date'].min()
        if date_range.days < 30:
            issues.append(f"Short date range: {date_range.days} days")
            recommendations.append("Consider collecting more historical data")
    
    # Check for duplicates
    if 'date' in df.columns and 'sku_id' in df.columns:
        duplicates = df.duplicated(subset=['date', 'sku_id']).sum()
        if duplicates > 0:
            issues.append(f"Duplicate date-SKU combinations: {duplicates} rows")
            recommendations.append("Aggregate or remove duplicate records")
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues,
        'recommendations': recommendations,
        'shape': df.shape,
        'date_range': (df['date'].min(), df['date'].max()) if 'date' in df.columns else None
    }

