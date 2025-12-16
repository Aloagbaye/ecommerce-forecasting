"""
Generate synthetic e-commerce sales data for tutorial purposes.

Usage:
    python scripts/generate_sample_data.py --output data/raw/sample_sales.csv --days 730 --skus 100
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


def generate_sample_data(
    n_days: int = 730,
    n_skus: int = 100,
    start_date: Optional[str] = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic e-commerce sales data with realistic patterns.
    
    Parameters
    ----------
    n_days : int
        Number of days of data to generate
    n_skus : int
        Number of unique SKUs
    start_date : str, optional
        Start date in YYYY-MM-DD format. Defaults to 2 years ago.
    seed : int
        Random seed for reproducibility
        
    Returns
    -------
    pd.DataFrame
        Generated sales data
    """
    np.random.seed(seed)
    
    # Set start date
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=n_days)).strftime('%Y-%m-%d')
    
    dates = pd.date_range(start=start_date, periods=n_days, freq='D')
    
    # Define categories and subcategories
    categories = {
        'Electronics': ['Phones', 'Laptops', 'Accessories', 'Audio'],
        'Clothing': ['Men', 'Women', 'Kids', 'Accessories'],
        'Home & Garden': ['Furniture', 'Decor', 'Tools', 'Outdoor'],
        'Sports': ['Fitness', 'Outdoor', 'Team Sports', 'Water Sports'],
        'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Children']
    }
    
    # Generate SKU data
    sku_data = []
    sku_id = 1
    
    for category, subcategories in categories.items():
        n_category_skus = n_skus // len(categories)
        for _ in range(n_category_skus):
            subcategory = np.random.choice(subcategories)
            base_price = np.random.uniform(10, 200)
            base_demand = np.random.uniform(5, 50)
            
            sku_data.append({
                'sku_id': f'SKU{sku_id:03d}',
                'category': category,
                'subcategory': subcategory,
                'base_price': base_price,
                'base_demand': base_demand
            })
            sku_id += 1
    
    # Generate sales records
    records = []
    
    for date in dates:
        day_of_week = date.dayofweek
        month = date.month
        day_of_month = date.day
        
        # Day of week effect (weekends higher)
        day_multiplier = 1.2 if day_of_week >= 5 else 1.0
        
        # Monthly seasonality (holiday months higher)
        if month in [11, 12]:  # Nov, Dec
            month_multiplier = 1.5
        elif month in [6, 7]:  # Summer
            month_multiplier = 1.2
        else:
            month_multiplier = 1.0
        
        # Long-term trend (slight growth)
        days_from_start = (date - dates[0]).days
        trend = 1 + (days_from_start / n_days) * 0.2
        
        for sku_info in sku_data:
            sku_id = sku_info['sku_id']
            base_demand = sku_info['base_demand']
            base_price = sku_info['base_price']
            
            # Random variation
            random_factor = np.random.lognormal(0, 0.3)
            
            # Promotion (10% chance)
            is_promotion = np.random.random() < 0.1
            promo_multiplier = 1.5 if is_promotion else 1.0
            
            # Calculate demand
            demand = base_demand * day_multiplier * month_multiplier * trend * random_factor * promo_multiplier
            units_sold = max(0, int(np.round(demand)))
            
            # Price variation (discounts during promotions)
            if is_promotion:
                price = base_price * np.random.uniform(0.7, 0.9)
            else:
                price = base_price * np.random.uniform(0.95, 1.05)
            
            # Some days have zero sales (stockouts, low demand)
            if np.random.random() < 0.15:  # 15% chance of zero
                units_sold = 0
            
            records.append({
                'date': date,
                'sku_id': sku_id,
                'category': sku_info['category'],
                'subcategory': sku_info['subcategory'],
                'price': round(price, 2),
                'units_sold': units_sold,
                'revenue': round(price * units_sold, 2),
                'promotion_flag': is_promotion,
                'stock_available': np.random.randint(0, 200)  # Random stock level
            })
    
    df = pd.DataFrame(records)
    
    return df


def main():
    parser = argparse.ArgumentParser(description='Generate sample e-commerce sales data')
    parser.add_argument(
        '--output',
        type=str,
        default='data/raw/sample_sales.csv',
        help='Output file path'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=730,
        help='Number of days of data to generate'
    )
    parser.add_argument(
        '--skus',
        type=int,
        default=100,
        help='Number of unique SKUs'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        default=None,
        help='Start date (YYYY-MM-DD). Defaults to N days ago.'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility'
    )
    
    args = parser.parse_args()
    
    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate data
    print(f"Generating {args.days} days of data for {args.skus} SKUs...")
    df = generate_sample_data(
        n_days=args.days,
        n_skus=args.skus,
        start_date=args.start_date,
        seed=args.seed
    )
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Data saved to: {output_path}")
    print(f"Shape: {df.shape}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Total revenue: ${df['revenue'].sum():,.2f}")
    print(f"Total units sold: {df['units_sold'].sum():,}")


if __name__ == '__main__':
    main()

