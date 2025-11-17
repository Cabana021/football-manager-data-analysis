import pytest
import sqlite3
import pandas as pd
from src.load.load import load_data

def test_load_data_creates_db_file(fixture_dados_transformados, tmp_path):
    test_db_path = tmp_path / "test_fm.db"
    load_data(fixture_dados_transformados, str(test_db_path), "players")
    assert test_db_path.exists()

def test_load_data_appends_data(fixture_dados_transformados, tmp_path):
    test_db_path = tmp_path / "test_fm_append.db"
    table_name = "players"
    
    # Primeira Carga 
    load_data(fixture_dados_transformados, str(test_db_path), table_name)
    
    # Segunda Carga 
    load_data(fixture_dados_transformados, str(test_db_path), table_name)
    
    # Verificação 
    with sqlite3.connect(test_db_path) as conn:
        df_from_db = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        
    assert len(df_from_db) == len(fixture_dados_transformados) * 2
    assert len(df_from_db) == 6 
