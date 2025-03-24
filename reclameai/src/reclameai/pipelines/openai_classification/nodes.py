"""
This is a boilerplate pipeline 'openai_classification'
generated using Kedro 0.19.12
"""
import os
import pandas as pd
import re
import matplotlib.pyplot as plt
from .prompt_util import create_classification_prompt
from .openai_util import send_request

def load_data(data: pd.DataFrame) -> pd.DataFrame:
    return data

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicatas, valores ausentes e limpa os textos."""
    df = df.drop_duplicates()
    df = df.dropna(subset=["Relato"])

    def clean_text(text):
        text = str(text).strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s,.!?-]", "", text)
        return text

    df["Relato"] = df["Relato"].apply(clean_text)
    return df

def group_reports(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa os relatos por ocorrência."""
    return df.groupby("Ocorrencia", as_index=False).agg(
        lambda x: "\n### ".join(x.astype(str)) if x.name == "Relato" else x.iloc[0]
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
    results = df["Relato"].apply(lambda relato: classify_complaint(relato, categorias))
    
    # Descompacta os resultados em duas colunas: 'categoria' e 'resumo'
    df["categoria"], df["resumo"] = zip(*results)

    return df

def save_results(df: pd.DataFrame) -> pd.DataFrame:
    """Salva os resultados classificados no dataset de saída."""
    return df

def plot_histogram(df: pd.DataFrame) -> plt.Figure:
    """Gera um histograma da coluna 'categoria' e retorna o objeto do gráfico."""
    fig, ax = plt.subplots(figsize=(10, 6))
    df["categoria"].value_counts().plot(kind="bar", color="skyblue", ax=ax)
    ax.set_title("Distribuição de Categorias")
    ax.set_xlabel("Categorias")
    ax.set_ylabel("Frequência")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig 

def consolidate_reports(output_dir: str, consolidated_filename: str, classificated_data: pd.DataFrame):
    """Consolida os totais de tokens e custos de todos os relatórios individuais."""
    consolidated_filepath = os.path.join(output_dir, consolidated_filename)
    os.makedirs(output_dir, exist_ok=True)

    total_prompt_tokens = 0
    total_response_tokens = 0
    total_cost = 0.0

    # Processa cada relatório individual
    for filename in os.listdir(output_dir):
        if filename.endswith(".txt") and filename != consolidated_filename:
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "r", encoding="utf-8") as individual_file:
                content = individual_file.read()

                # Extrai os valores de tokens e custo do conteúdo do relatório
                for line in content.splitlines():
                    if line.startswith("Tokens usados no prompt:"):
                        total_prompt_tokens += int(line.split(":")[1].strip())
                    elif line.startswith("Tokens usados na resposta:"):
                        total_response_tokens += int(line.split(":")[1].strip())
                    elif line.startswith("Custo estimado:"):
                        total_cost += float(line.split(":")[1].strip().replace("$", ""))

    # Salva os totais no arquivo consolidado
    with open(consolidated_filepath, "w", encoding="utf-8") as consolidated_file:
        consolidated_file.write("Resumo Total:\n")
        consolidated_file.write(f"Tokens totais no prompt: {total_prompt_tokens}\n")
        consolidated_file.write(f"Tokens totais na resposta: {total_response_tokens}\n")
        consolidated_file.write(f"Tokens totais: {total_prompt_tokens + total_response_tokens}\n")
        consolidated_file.write(f"Custo total estimado: ${total_cost:.6f}\n")

    print(f"Relatório consolidado salvo em: {consolidated_filepath}") 

