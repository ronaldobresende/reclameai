def create_classification_prompt(historico, classificacoes, prompt_base):
    """Cria o prompt para classificar e resumir reclamações."""
    categorias = "\n    - ".join(classificacoes)
    return prompt_base.format(categorias=categorias, historico=historico)
