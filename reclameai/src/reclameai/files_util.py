import awswrangler as wr
import pandas as pd
from io import BytesIO
import docx

def ler_csv_s3(s3_path: str) -> pd.DataFrame:
    """
    Lê um arquivo CSV do S3 e retorna um DataFrame.
    """
    try:
        df = wr.s3.read_csv(path=s3_path)
        print(f"Arquivo CSV lido com sucesso de {s3_path}")
        return df
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo CSV do S3: {str(e)}")

def ler_excel_s3(s3_path: str, sheet_name=0) -> pd.DataFrame:
    """
    Lê um arquivo Excel (.xlsx) do S3 e retorna um DataFrame.
    """
    try:
        df = wr.s3.read_excel(path=s3_path, sheet_name=sheet_name)
        print(f"Arquivo Excel lido com sucesso de {s3_path}")
        return df
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo Excel do S3: {str(e)}")

def ler_docx_s3(s3_path: str) -> str:
    """
    Lê um arquivo Word (.docx) do S3 e retorna o texto completo.
    """
    import boto3
    s3 = boto3.client('s3')
    bucket, key = s3_path.replace("s3://", "").split("/", 1)
    obj = s3.get_object(Bucket=bucket, Key=key)
    doc = docx.Document(BytesIO(obj['Body'].read()))
    texto = "\n".join([p.text for p in doc.paragraphs])
    print(f"Arquivo DOCX lido com sucesso de {s3_path}")
    return texto