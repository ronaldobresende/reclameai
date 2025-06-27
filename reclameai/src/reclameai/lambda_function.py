import awswrangler as wr
import re
import pandas as pd
from openai_util import send_request
from prompt_util import create_classification_prompt   
from utils import save_parquet_and_update_glue 
from utils import load_yaml_s3

def load_data(database, table, partition_filter):
    """
    Carrega os dados do Athena com base no filtro de partição.
    """
    try:
        # Construindo a consulta SQL com filtro de partição
        query = f"""
        SELECT *
        FROM {database}.{table}
        WHERE {partition_filter}
        """

        # Executando a consulta no Athena
        df = wr.athena.read_sql_query(
            sql=query,
            database=database
        )
        return df

    except Exception as e:
        raise Exception(f"Erro ao carregar os dados: {str(e)}")
    
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicatas, valores ausentes e limpa os textos."""
    df = df.drop_duplicates()
    df = df.dropna(subset=["relato"])

    def clean_text(text):
        text = str(text).strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s,.!?-]", "", text)
        return text

    df["relato"] = df["relato"].apply(clean_text)
    return df   

def group_reports(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa os relatos por ocorrência."""
    return df.groupby("ocorrencia", as_index=False).agg(
        lambda x: "\n### ".join(x.astype(str)) if x.name == "relato" else x.iloc[0]
    )

def classify_complaint(historico, categorias, config):
    """Classifica uma única ocorrência com base no histórico completo e gera um resumo."""
    # Cria o prompt para classificar e resumir
    prompt = create_classification_prompt(historico, categorias, config["prompt_classificacao"])
    
    # Envia o prompt para a API da OpenAI
    openai_response = send_request(prompt,config["openai"]["model"], config["openai"]["temperature"], config["openai"]["top_p"])
    response = openai_response.strip()

    # Divide a resposta em classificação e resumo
    classification = None
    summary = None
    if "Classificação:" in response and "Resumo:" in response:
        parts = response.split("Resumo:")
        classification = parts[0].replace("Classificação:", "").strip()
        summary = parts[1].strip()

    return classification, summary

def classify_complaints(df: pd.DataFrame, categorias: list, config) -> pd.DataFrame:
    """Classifica as reclamações e gera resumos usando a API da OpenAI."""
    
    # Aplica a função de classificação e resumo ao DataFrame
    results = df["relato"].apply(lambda relato: classify_complaint(relato, categorias,config))
    
    # Descompacta os resultados em duas colunas: 'categoria' e 'resumo'
    df["categoria"], df["resumo"] = zip(*results)

    return df

def save_to_glue_catalog(df: pd.DataFrame, database: str, table: str, s3_path: str):
    save_parquet_and_update_glue(
        df=df,
        bucket=s3_path,
        prefix="tabela_classificada", 
        database=database,
        table=table,
        partition_col="anomesdia"
    )    
    
def lambda_handler(event, context):
    """
    Função Lambda para carregar dados do Athena e retornar um DataFrame.
    """
    # Caminho no S3 onde os dados serão salvos
    s3_path = "s3-768471683026-sor"

    # Configurações do Athena e Glue Catalog
    database = "db_reclameai"
    table = "tb_reclamacoes_original"
    partition_filter = "anomesdia >= '20241001'"
    config = load_yaml_s3(s3_path + "/parameters.yaml")

    try:
        # Carregando os dados usando a função load_data
        df = load_data(database, table, partition_filter)

        # Limpando os dados usando a função clean_data
        df = clean_data(df)

        # Agrupando os relatos por ocorrência
        df = group_reports(df)  

        # Lista de categorias
        categorias = config["categorias"]
        print("Categorias carregadas do YAML:", categorias)

        # Chamando a função classify_complaints com o DataFrame e a lista de categorias
        df_classificado = classify_complaints(df, categorias, config)

        anomesdia = pd.to_datetime(df['data'].iloc[0]).strftime('%Y%m%d')

        # Salvar o DataFrame classificado no Glue Catalog
        save_parquet_and_update_glue(
            df=df_classificado,
            anomesdia=anomesdia,
            bucket=s3_path,
            prefix="tabela_classificada", 
            database="db_reclameai",
            table="reclamacoes_classificadas",
            partition_col="anomesdia"
        )          

        return df_classificado
    except Exception as e:
        raise Exception(f"Erro ao processar os dados: {str(e)}")