import pandas as pd
import sys

# Extrai dados de um arquivo .CSV
def extract_data(file_path: str) -> pd.DataFrame:
    print(f"Iniciando extração de dados de: {file_path}")
    try:
        # Lê o CSV com os parâmetros específicos do Football Manager
        df = pd.read_csv(
            file_path, 
            sep=';', 
            encoding='latin1'
        )
        
        print("Dados extraídos com sucesso. Retornando DataFrame bruto.")
        return df

    except FileNotFoundError:
        print(f"Erro: O arquivo não foi encontrado em '{file_path}'.", file=sys.stderr)
        raise
        
    except Exception as e:
        print(f"Um erro inesperado ocorreu durante a extração: {e}", file=sys.stderr)
        raise

if __name__ == '__main__':
    # Bloco para teste local (python src/extract/extract.py)
    try:
        test_path = 'data/raw/jogadores-brasileiros.csv' 
        print(f"--- Testando Módulo Extract ---")
        df_bruto = extract_data(test_path)
        print("\n--- Informações do DataFrame Bruto (Teste) ---")
        print(df_bruto.info())
        print("\n--- Amostra (head) do DataFrame Bruto (Teste) ---")
        print(df_bruto.head())
        print("--- Teste do Módulo Extract Concluído ---")

    except FileNotFoundError:
        print("Teste falhou: Arquivo de teste não encontrado.")
    except Exception as e:
        print(f"Teste falhou com erro: {e}")
