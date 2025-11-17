import pandas as pd
import numpy as np 
import re

# Converte valores monetários do Football Manager
def convert_currency_to_float(valor) -> float:
    if isinstance(valor, (int, float)) or pd.isna(valor):
        return valor

    s = str(valor).strip().upper()

    if not s or s == '-' or s == 'N/D':
        return np.nan

    s = s.replace('R$', '').replace('P/S', '').strip()
    s = s.replace('.', '')
    s = s.replace(',', '.')

    multiplicador = 1.0
    if s.endswith('M'):
        multiplicador = 1_000_000.0
        s = s[:-1] 
    elif s.endswith('K'):
        multiplicador = 1_000.0
        s = s[:-1] 
    
    try:
        return float(s) * multiplicador
    except ValueError:
        return np.nan

# Converte classificações do FM (ex: "53,7%") para um float (ex: 53.7).
def convert_rating_to_float(valor) -> float:
    if isinstance(valor, (int, float)) or pd.isna(valor):
        return valor
    
    s = str(valor).split(' ')[0]
    s = s.replace('%', '').replace(',', '.')
    
    try:
        return float(s)
    except ValueError:
        return np.nan

# Extrai o sufixo entre parênteses (ex: "FS" ou "W")
def extract_rating_suffix(valor) -> str:
    if pd.isna(valor) or not isinstance(valor, str):
        return np.nan

    match = re.search(r'\((.*?)\)', valor)

    if match:
        return match.group(1) 
    else:
        return np.nan 

# --- Bloco de Teste ---
if __name__ == '__main__':
    # Bloco para teste local (python src/utils.py)
    print("--- Testando Módulo Utils ---")
    
    # Testes de Moeda
    print("\n--- Testes de Moeda ---")
    testes_moeda = ['R$ 1,5M', 'R$ 500K', 'R$ 1.250', 0, 'R$ 1.250.000', 'N/D', np.nan]
    for teste in testes_moeda:
        print(f"'{teste}' -> {convert_currency_to_float(teste)}")

    # Testes de Classificação
    print("\n--- Testes de Classificação ---")
    testes_rating = ['53,7% (M)', '49,4% (Pnt)', '70,1%', 80.0, np.nan]
    for teste in testes_rating:
        print(f"'{teste}' -> {convert_rating_to_float(teste)}")

    # Testes de Sufixo
    print("\n--- Testes de Classificação (Suffix) ---")
    testes_suffix = ['95.6% (FS)', '72.2% (W)', '96.5% (W)', '70,1%', 80.0, np.nan]
    for teste in testes_suffix:
        print(f"'{teste}' -> {extract_rating_suffix(teste)}")
