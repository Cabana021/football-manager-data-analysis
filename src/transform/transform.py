import pandas as pd
import datetime
import sys
from src.utils import convert_currency_to_float, convert_rating_to_float, extract_rating_suffix

# Transformação completo nos dados brutos do FM.
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    print("Iniciando processo de transformação...")
    
    df_limpo = df.copy()

    # 1. Remoção de Lixo 
    linhas_antes = len(df_limpo)
    df_limpo = df_limpo.dropna(subset=['Nome']).reset_index(drop=True)
    linhas_depois = len(df_limpo)
    print(f"Removidos {linhas_antes - linhas_depois} 'jogadores fantasmas'.")

    # 2. Seleção e Renomeação de Colunas 
    colunas_map = {
    # Informações básicas
    'Nome': 'nome',
    'País': 'pais',
    'Posição': 'posicao',
    'Clube': 'clube',
    'Idade': 'idade',
    'Salário': 'salario',
    'Valor Venda': 'valor',
    'Melhor Classificação': 'classificacao_atual',
    'Melhor Classificação Potencial': 'classificacao_potencial',
}
    
    df_limpo = df_limpo[list(colunas_map.keys())]
    df_limpo = df_limpo.rename(columns=colunas_map)

    # 3. Limpeza de Tipos de Dados
    print("Aplicando limpeza de tipos de dados (moeda e classificações)...")
    
    df_limpo['sufixo_atual'] = df_limpo['classificacao_atual'].apply(extract_rating_suffix)
    df_limpo['sufixo_potencial'] = df_limpo['classificacao_potencial'].apply(extract_rating_suffix)
    df_limpo['valor'] = df_limpo['valor'].apply(convert_currency_to_float)
    df_limpo['salario'] = df_limpo['salario'].apply(convert_currency_to_float)
    df_limpo['classificacao_atual'] = df_limpo['classificacao_atual'].apply(convert_rating_to_float)
    df_limpo['classificacao_potencial'] = df_limpo['classificacao_potencial'].apply(convert_rating_to_float)

    # 4. Tratamento de Nulos (NaN)
    print("Tratando valores nulos restantes...")
    df_limpo['valor'] = df_limpo['valor'].fillna(0)
    df_limpo['salario'] = df_limpo['salario'].fillna(0)

    # Data para usar de comparação
    print("Adicionando data do snapshot...")
    df_limpo['data_snapshot'] = datetime.datetime.now()
    
    # 5. Definir os Tipos de Dados Finais 
    tipos_finais = {
        'nome': 'object',
        'pais': 'object',
        'posicao': 'object',
        'clube': 'object',
        'idade': 'int64',
        'valor': 'float64',
        'salario': 'float64',
        'classificacao_atual': 'float64',
        'classificacao_potencial': 'float64',
        'data_snapshot': 'datetime64[ns]',
        'sufixo_atual': 'object', 
        'sufixo_potencial': 'object'
    }
    df_limpo = df_limpo.astype(tipos_finais)

    print(f"Transformação concluída. DataFrame final com {len(df_limpo)} linhas.")
    
    return df_limpo

# --- Bloco de Teste ---
if __name__ == '__main__':
    # Bloco para teste local (python src/transform/transform.py)
    try:
        sys.path.append('.') 
        from src.extract.extract import extract_data
        
        print("--- Testando Módulo Transform ---")
        
        # 1. Extrair
        test_path = 'data/Raw/brasil-players.csv'
        df_bruto = extract_data(test_path)
        
        print("\n--- Informações do DataFrame Bruto ---")
        print(df_bruto.info())
        
        # 2. Transformar
        df_transformado = transform_data(df_bruto)
        
        print("\n--- Informações do DataFrame Transformado ---")
        df_transformado.info()
        
        print("\n--- Amostra (head) do DataFrame Transformado ---")
        print(df_transformado.head())
        
        print("\n--- Verificando Valores (head) ---")
        print(df_transformado[['valor', 'salario', 'classificacao_atual']].head())
        
        print("--- Teste do Módulo Transform Concluído ---")

    except ImportError:
        print("Erro: Não foi possível importar 'src.extract.extract'.")
        print("Rode este script do diretório raiz do projeto.")
    except FileNotFoundError:
        print(f"Erro: Arquivo de teste não encontrado em '{test_path}'.")
    except Exception as e:
        print(f"Um erro ocorreu durante o teste: {e}")
