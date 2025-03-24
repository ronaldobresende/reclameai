import os
from openai import OpenAI
import tiktoken
from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project

# Inicializa o projeto Kedro e carrega o contexto
bootstrap_project(os.getcwd())
with KedroSession.create(project_path=os.getcwd()) as session:
    context = session.load_context()
    params = context.params["openai"]

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def count_tokens(prompt, model="gpt-4o"):
    """Conta o número de tokens no prompt usando tiktoken."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(prompt))

def send_request(prompt, model="gpt-4o", report_id=None):
    """Envia o prompt para a API da OpenAI, conta os tokens e calcula o custo."""
    # Conta os tokens do prompt
    prompt_tokens = count_tokens(prompt, model)

    # Envia o prompt para a API
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    resposta = response.choices[0].message.content

    # Conta os tokens da resposta
    response_tokens = count_tokens(resposta, model)

    # Calcula o custo total
    total_tokens = prompt_tokens + response_tokens
    cost = total_tokens * params["token_prices"][model]

    report_content = (
        f"Tokens usados no prompt: {prompt_tokens}\n"
        f"Tokens usados na resposta: {response_tokens}\n"
        f"Tokens totais: {total_tokens}\n"
        f"Custo estimado: ${cost:.6f}\n"
    )

    # Salva o relatório acumulando os dados
    if report_id is None:
        report_id = f"report_{os.getpid()}_{prompt_tokens}"
    save_report(report_content, f"{report_id}.txt")
 
    return resposta

def save_report(report_content: str, filename: str):
    """Salva o relatório no diretório configurado."""
    output_dir = params["output_dir"]
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Relatório salvo em: {filepath}")