import json
from lambda_function import lambda_handler

# Simulando o evento e o contexto
event = {}
context = {}

try:
    # Executando a função Lambda
    df = lambda_handler(event, context)

    # Convertendo o DataFrame para JSON
    data = df.to_dict(orient="records")
    print(json.dumps(data, indent=4))

except Exception as e:
    print(f"Erro ao executar a função: {str(e)}")