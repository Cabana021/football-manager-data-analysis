import pytest
import pandas as pd
import numpy as np
from src.utils import convert_currency_to_float, convert_rating_to_float

def test_convert_currency_to_float():
    assert convert_currency_to_float('R$ 1,5M') == 1500000.0 
    assert convert_currency_to_float('R$ 500K') == 500000.0
    assert convert_currency_to_float('R$ 1.250') == 1250.0
    assert convert_currency_to_float('R$ 1.250.000') == 1250000.0
    assert convert_currency_to_float('0') == 0.0
    assert convert_currency_to_float(0) == 0.0
    assert pd.isna(convert_currency_to_float('N/D'))
    assert pd.isna(convert_currency_to_float(np.nan))

def test_convert_rating_to_float():
    assert convert_rating_to_float('50,1% (M)') == 50.1
    assert convert_rating_to_float('45,0%') == 45.0
    assert convert_rating_to_float('70,0%') == 70.0
    assert pd.isna(convert_rating_to_float('N/D')) 
