import pytest
import pandas as pd

def test_remove_ghosts(fixture_dados_transformados):
    assert len(fixture_dados_transformados) == 3

def test_column_renaming_and_selection(fixture_dados_transformados):
    colunas_esperadas = [
        'nome', 
        'pais', 
        'posicao', 
        'clube', 
        'idade', 
        'valor',
        'salario', 
        'classificacao_atual', 
        'classificacao_potencial', 
        'sufixo_atual', 
        'sufixo_potencial',
        'data_snapshot'
    ]
    assert set(fixture_dados_transformados.columns) == set(colunas_esperadas)

def test_currency_conversion_in_transform(fixture_dados_transformados):
    valor_rico = fixture_dados_transformados.loc[
        fixture_dados_transformados['nome'] == 'Jogador B (Rico)', 'valor'
    ].iloc[0]
    assert valor_rico == 500000.0

def test_rating_conversion_in_transform(fixture_dados_transformados):
    classificacao_a = fixture_dados_transformados.loc[
        fixture_dados_transformados['nome'] == 'Jogador A', 'classificacao_atual'
    ].iloc[0]
    assert classificacao_a == 50.1

def test_data_snapshot_column(fixture_dados_transformados):
    assert 'data_snapshot' in fixture_dados_transformados.columns
    assert pd.api.types.is_datetime64_any_dtype(
        fixture_dados_transformados['data_snapshot']
    )
