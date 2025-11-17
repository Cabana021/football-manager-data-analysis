import sys
import os
from src.extract.extract import extract_data
from src.transform.transform import transform_data
from src.load.load import load_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'todos-jogadores.csv')
DB_PATH = os.path.join(BASE_DIR, 'database', 'fm_database.db')

# Nome da tabela no banco
TABLE_NAME = 'players'

# Função principal que orquestra o pipeline ETL.
def main():
    print("==========================================")
    print("INICIANDO O PIPELINE ETL DO PROJETO FM")
    print("==========================================")
    
    try:
        # 1. EXTRACT
        print("\n[Passo 1/3] Extraindo dados brutos...")
        df_bruto = extract_data(DATA_PATH)
        print(f"✔ Sucesso: {len(df_bruto)} registros brutos extraídos.")
        
        # 2. TRANSFORM 
        print("\n[Passo 2/3] Transformando e limpando os dados...")
        df_transformado = transform_data(df_bruto)
        print(f"✔ Sucesso: {len(df_transformado)} registros limpos e prontos.")
        
        # 3. LOAD
        print("\n[Passo 3/3] Carregando dados para o Banco de Dados...")
        load_data(df_transformado, DB_PATH, TABLE_NAME)
        print(f"✔ Sucesso: Dados salvos em '{TABLE_NAME}' no arquivo '{DB_PATH}'.")
        
        print("\n=============================================")
        print("--- PIPELINE ETL CONCLUÍDO COM SUCESSO! ---")
        print("===============================================")

    except FileNotFoundError:
        print(f"\n[ERRO FATAL] O arquivo de dados não foi encontrado em:", file=sys.stderr)
        print(f"{DATA_PATH}", file=sys.stderr)
        print("Verifique se o arquivo .csv está no local correto.", file=sys.stderr)
    except Exception as e:
        print(f"\n[ERRO FATAL] O pipeline falhou.", file=sys.stderr)
        print(f"Detalhe do erro: {e}", file=sys.stderr)
        
if __name__ == "__main__":
    main()
