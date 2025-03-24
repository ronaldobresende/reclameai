
def create_classification_prompt(historico, classificacoes):
    """Cria o prompt para classificar e resumir reclamações."""
    categorias = "\n    - ".join(classificacoes)
    prompt = f"""
    Analise o seguinte histórico de atendimento e realize as seguintes tarefas:
    
    1. Classifique o problema principal em uma das seguintes categorias:
    - {categorias}

    2. Gere um resumo detalhado do histórico, destacando os principais pontos e possíveis problemas.

    Cada atualização no histórico é separada por "###".

    Histórico:
    ### {historico}

    Responda no seguinte formato:
    Classificação: <categoria>
    Resumo: <resumo>
    """
    return prompt.strip()