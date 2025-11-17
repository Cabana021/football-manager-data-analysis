import pytest
import pandas as pd
import numpy as np
from src.transform.transform import transform_data

# Simula os dados reais do CSV.
@pytest.fixture(scope="session")
def fixture_dados_brutos() -> pd.DataFrame:
    dados = {
        'Nome': ['Jogador A', 'Jogador B (Rico)', 'Jogador C (Bom)', np.nan],
        'País': ['Brasil', 'Brasil', 'Argentina', 'Brasil'],
        'Posição': ['PL', 'M C', 'DC', 'GK'],
        'Clube': ['Clube X', 'Clube Y', 'Clube Z', '-'],
        'Idade': [22, 25, 28, 16],
        'Valor Venda': ['R$ 1.5M', 'R$ 500K', '0', 'R$ 1.250'],
        'Salário': ['R$ 150K', 'R$ 20K', '0', '0'],
        'Melhor Classificação': ['50,1% (M)', '45,0%', '60,0%', 'N/D'],
        'Melhor Classificação Potencial': ['70,0% (M)', '45,0%', '60,0%', 'N/D'],
        'Coluna Inutil 1': [1, 2, 3, 4],
        'Coluna Inutil 2': ['a', 'b', 'c', 'd']
    }
    return pd.DataFrame(dados)

# Pega os dados brutos, aplica a transformação e retorna o DataFrame limpo.
@pytest.fixture(scope="session")
def fixture_dados_transformados(fixture_dados_brutos) -> pd.DataFrame:
    return transform_data(fixture_dados_brutos)
