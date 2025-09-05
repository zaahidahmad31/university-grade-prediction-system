# Create this file at backend/utils/helpers.py

from decimal import Decimal
from typing import Union

def safe_float(value: Union[float, Decimal, None]) -> float:
    """Safely convert a value to float, handling Decimal types"""
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)

def safe_int(value: Union[int, Decimal, None]) -> int:
    """Safely convert a value to int, handling Decimal types"""
    if value is None:
        return 0
    if isinstance(value, Decimal):
        return int(value)
    return int(value)