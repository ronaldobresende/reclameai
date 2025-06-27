import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import boto3
import io
import datetime
import yaml

def save_parquet_and_update_glue(df, anomesdia, bucket, prefix, database, table, partition_col="anomesdia"):
    """
    Salva DataFrame como Parquet no S3 e registra a partição no Glue Catalog.
    Se a partição já existir, substitui os dados.
    """
    # # 1. Gerar partição atual
    # hoje = datetime.date.today()
    # anomesdia = hoje.strftime("%Y%m%d")
    # df[partition_col] = anomesdia

    # 2. Caminho S3 particionado
    s3_prefix_part = f"{prefix}/{partition_col}={anomesdia}/"
    s3_key = f"{s3_prefix_part}dados.parquet"
    s3_uri = f"s3://{bucket}/{s3_key}"

    # 3. Excluir arquivos antigos do S3 para a partição
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket, Prefix=s3_prefix_part)
    if "Contents" in response:
        for obj in response["Contents"]:
            s3.delete_object(Bucket=bucket, Key=obj["Key"])
        print(f"🗑️ Arquivos antigos removidos de: s3://{bucket}/{s3_prefix_part}")

    # 4. Excluir partição antiga do Glue (se existir)
    glue = boto3.client("glue")
    try:
        glue.delete_partition(DatabaseName=database, TableName=table, PartitionValues=[anomesdia])
        print(f"🗑️ Partição antiga removida do Glue: {database}.{table} - {anomesdia}")
    except glue.exceptions.EntityNotFoundException:
        pass  # Partição não existia

    # 5. Escrever novo Parquet em memória
    table_arrow = pa.Table.from_pandas(df)
    buf = io.BytesIO()
    pq.write_table(table_arrow, buf, compression='snappy')
    buf.seek(0)

    # 6. Enviar novo arquivo para o S3
    s3.upload_fileobj(buf, Bucket=bucket, Key=s3_key)
    print(f"✅ Arquivo gravado em: {s3_uri}")

    # 7. Registrar a nova partição no Glue Catalog
    glue.create_partition(
        DatabaseName=database,
        TableName=table,
        PartitionInput={
            'Values': [anomesdia],
            'StorageDescriptor': {
                'Columns': [
                    {'Name': col, 'Type': 'string'}
                    for col in df.columns if col != partition_col
                ],
                'Location': f"s3://{bucket}/{s3_prefix_part}",
                'InputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
                'OutputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat',
                'SerdeInfo': {
                    'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
                    'Parameters': {'serialization.format': '1'}
                }
            },
            'Parameters': {},
        }
    )

    print(f"✅ Partição {anomesdia} registrada no catálogo Glue: {database}.{table}")

def load_yaml_s3(s3_path):
    s3 = boto3.client('s3')
    bucket, key = s3_path.replace("s3://", "").split("/", 1)
    obj = s3.get_object(Bucket=bucket, Key=key)
    return yaml.safe_load(obj['Body'].read().decode())

