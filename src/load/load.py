import pandas as pd
import sqlite3
import sys
import os

# Carrega o DataFrame transformado em um banco de dados SQLite.
def load_data(df: pd.DataFrame, db_path: str, table_name: str) -> None:
    print(f"Iniciando carga de dados para: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        with sqlite3.connect(db_path) as conn:
            df.to_sql(
                table_name,
                conn,
                if_exists='append', 
                index=False          
            )
        
        print(f"Dados carregados com sucesso na tabela '{table_name}'.")

    except sqlite3.Error as e:
        print(f"Erro ao carregar dados para o SQLite: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Um erro inesperado ocorreu durante a carga: {e}", file=sys.stderr)
        raise

# --- Bloco de Teste ---
def _verify_load(db_path: str, table_name: str):
    print(f"\n--- Verificando Carga no DB ---")
    if not os.path.exists(db_path):
        print(f"Falha na verificação: Arquivo de DB '{db_path}' não encontrado.")
        return

    try:
        with sqlite3.connect(db_path) as conn:
            df_from_db = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        
        print(f"Sucesso! Tabela '{table_name}' lida do DB.")
        print(f"Total de linhas no DB: {len(df_from_db)}")
        print("\n--- Informações do DataFrame (do DB) ---")
        print(df_from_db.info())
        print("\n--- Amostra (head) do DataFrame (do DB) ---")
        print(df_from_db.head())
        print("--- Verificação Concluída ---")

    except Exception as e:
        print(f"Erro ao verificar o DB: {e}")

if __name__ == '__main__':
    try:
        sys.path.append('.')
        from src.extract.extract import extract_data
        from src.transform.transform import transform_data
        
        print("--- Testando Módulo Load (E-T-L Completo) ---")
        
        # --- CONSTANTES DE TESTE ---
        DATA_PATH = 'data/raw/brasil-players.csv'
        DB_PATH = 'database/fm_database.db' 
        TABLE_NAME = 'players'              
        
        # 1. Extrair
        df_bruto = extract_data(DATA_PATH)
        
        # 2. Transformar
        df_transformado = transform_data(df_bruto)
        
        # 3. Carregar
        load_data(df_transformado, DB_PATH, TABLE_NAME)
        
        # 4. Verificar 
        _verify_load(DB_PATH, TABLE_NAME)
        
        print("\n--- Teste E-T-L Concluído com Sucesso ---")

    except ImportError:
        print("Erro: Não foi possível importar 'src.extract' ou 'src.transform'.")
        print("Rode este script do diretório raiz do projeto.")
    except FileNotFoundError:
        print(f"Erro: Arquivo de dados não encontrado em '{DATA_PATH}'.")
    except Exception as e:
        print(f"Um erro ocorreu durante o teste E-T-L: {e}")
