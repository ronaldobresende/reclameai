import awswrangler as wr
import re
import pandas as pd
from openai_util import send_request
from prompt_util import create_classification_prompt    

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

def classify_complaint(historico, categorias):
    """Classifica uma única ocorrência com base no histórico completo e gera um resumo."""
    # Cria o prompt para classificar e resumir
    prompt = create_classification_prompt(historico, categorias)  
    
    # Envia o prompt para a API da OpenAI
    openai_response = send_request(prompt)
    response = openai_response.strip()

    # Divide a resposta em classificação e resumo
    classification = None
    summary = None
    if "Classificação:" in response and "Resumo:" in response:
        parts = response.split("Resumo:")
        classification = parts[0].replace("Classificação:", "").strip()
        summary = parts[1].strip()

    return classification, summary

def classify_complaints(df: pd.DataFrame, categorias: list) -> pd.DataFrame:
    """Classifica as reclamações e gera resumos usando a API da OpenAI."""
    
    # Aplica a função de classificação e resumo ao DataFrame
    results = df["relato"].apply(lambda relato: classify_complaint(relato, categorias))
    
    # Descompacta os resultados em duas colunas: 'categoria' e 'resumo'
    df["categoria"], df["resumo"] = zip(*results)

    return df

import awswrangler as wr

def save_to_glue_catalog(df: pd.DataFrame, database: str, table: str, s3_path: str):
    """
    Salva o DataFrame no S3 e atualiza o catálogo do Glue.
    """
    try:
        # Salvando o DataFrame no S3 e atualizando o catálogo do Glue
        wr.s3.to_parquet(
            df=df,
            path=s3_path,  
            dataset=True,
            database=database,
            table=table,
            mode="overwrite",  
            partition_cols=["anomesdia"]  # Atualiza as partições automaticamente
        )
        print(f"Dados salvos com sucesso na tabela {database}.{table} e catálogo atualizado.")
    except Exception as e:
        raise Exception(f"Erro ao salvar os dados no Glue Catalog: {str(e)}")

def lambda_handler(event, context):
    """
    Função Lambda para carregar dados do Athena e retornar um DataFrame.
    """
    # Configurações do Athena e Glue Catalog
    database = "db_reclameai"
    table = "tb_reclamacoes_original"
    partition_filter = "anomesdia >= '20241001'"

    try:
        # Carregando os dados usando a função load_data
        df = load_data(database, table, partition_filter)

        # Limpando os dados usando a função clean_data
        df = clean_data(df)

        # Agrupando os relatos por ocorrência
        df = group_reports(df)  

        # Lista de categorias
        categorias = [
            "Problema em saque",
            "Atendimento ruim",
            "Fraude bancária",
            "Cobrança indevida",
            "Cartão clonado",
            "PIX enviado errado",
            "Problema com fatura do cartão",
            "Problema com limite de crédito",
            "Problema no acesso ao app",
            "Débito não autorizado"
        ]

        # Chamando a função classify_complaints com o DataFrame e a lista de categorias
        df_classificado = classify_complaints(df, categorias)

        # return {
        #     "statusCode": 200,
        #     "body": df_classificado.to_json(orient="records")
        # }

        # Caminho no S3 onde os dados serão salvos
        s3_path = "s3://s3-768471683026-sor/"

        # Salvar o DataFrame classificado no Glue Catalog
        save_to_glue_catalog(df_classificado, "db_reclameai", "reclamacoes_classificadas", s3_path)        

        return df_classificado


    except Exception as e:
        raise Exception(f"Erro ao processar os dados: {str(e)}")