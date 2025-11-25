"""
Script to create test_data folder with sample expense data spanning 4 months.
Run this to regenerate test data: python create_test_data.py
"""

import json
import os
from datetime import datetime, timedelta
import random

# Categories for realistic test data
CATEGORIES = {
    'groceries': {'min': 20, 'max': 150, 'frequency': 0.25},
    'rent': {'min': 800, 'max': 1200, 'frequency': 0.05},
    'utilities': {'min': 50, 'max': 200, 'frequency': 0.08},
    'gas': {'min': 30, 'max': 80, 'frequency': 0.15},
    'dining': {'min': 15, 'max': 75, 'frequency': 0.20},
    'coffee': {'min': 3, 'max': 8, 'frequency': 0.12},
    'entertainment': {'min': 20, 'max': 100, 'frequency': 0.10},
    'shopping': {'min': 25, 'max': 200, 'frequency': 0.05},
}

def generate_expense(date, category, amount):
    """Generate a single expense entry."""
    return {
        "date": date.strftime("%Y-%m-%d"),
        "amount": round(amount, 2),
        "description": category
    }

def generate_month_data(year, month):
    """Generate expense data for a specific month."""
    expenses = []
    total = 0.0
    
    # Get number of days in month
    if month == 12:
        days_in_month = 31
    else:
        next_month = datetime(year, month + 1, 1)
        days_in_month = (next_month - timedelta(days=1)).day
    
    # Generate expenses throughout the month
    for day in range(1, days_in_month + 1):
        date = datetime(year, month, day)
        
        # Skip future dates
        if date > datetime.now():
            continue
        
        # Generate expenses based on category frequency
        for category, config in CATEGORIES.items():
            if random.random() < config['frequency']:
                amount = random.uniform(config['min'], config['max'])
                expense = generate_expense(date, category, amount)
                expenses.append(expense)
                total += amount
    
    # Add some one-time expenses
    one_time_expenses = [
        ('rent', 1000),
        ('utilities', 120),
        ('shopping', 150),
    ]
    
    for category, amount in one_time_expenses:
        # Add on a random day in the first week
        day = random.randint(1, min(7, days_in_month))
        date = datetime(year, month, day)
        if date <= datetime.now():
            expense = generate_expense(date, category, amount)
            expenses.append(expense)
            total += amount
    
    # Sort by date
    expenses.sort(key=lambda x: x['date'])
    
    return expenses, round(total, 2)

def create_test_data_folder():
    """Create test_data folder with sample data for 4 months."""
    test_data_dir = "test_data"
    
    # Create test_data directory
    if not os.path.exists(test_data_dir):
        os.makedirs(test_data_dir)
        print(f"Created {test_data_dir} directory")
    
    # Generate data for August, September, October, November 2025
    months = [
        (2025, 8),   # August
        (2025, 9),   # September
        (2025, 10),  # October
        (2025, 11),  # November
    ]
    
    for year, month in months:
        month_key = f"{year}-{month:02d}"
        data_folder = os.path.join(test_data_dir, f"data_{month_key}")
        
        # Create month folder
        os.makedirs(data_folder, exist_ok=True)
        
        # Generate expenses
        expenses, total = generate_month_data(year, month)
        
        # Create expenses.json
        expenses_file = os.path.join(data_folder, "expenses.json")
        data = {
            "expenses": expenses,
            "monthly_total": total
        }
        
        with open(expenses_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Created {month_key}: {len(expenses)} expenses, ${total:.2f} total")
    
    # Create .gitkeep for temp_AI folder (will be created by AI system if needed)
    temp_ai_dir = os.path.join(test_data_dir, "temp_AI")
    if not os.path.exists(temp_ai_dir):
        os.makedirs(temp_ai_dir)
        with open(os.path.join(temp_ai_dir, ".gitkeep"), 'w') as f:
            f.write("# Temporary AI processing files\n")
        print(f"Created {temp_ai_dir} directory for AI temp files")
    
    print(f"\nTest data created successfully in {test_data_dir}/")
    print("Months: 2025-08, 2025-09, 2025-10, 2025-11")

if __name__ == "__main__":
    create_test_data_folder()

