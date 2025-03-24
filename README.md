
# ReclameAI

ReclameAI é uma aplicação que processa e analisa reclamações de clientes e dados de NPS (Net Promoter Score), utilizando a API da OpenAI para **resumir**, **classificar** e **agrupar** as reclamações por tipo. O projeto é desenvolvido em **Python** e utiliza o **Kedro** para orquestrar o pipeline de dados, automatizando o processamento e fornecendo insights sobre áreas de melhoria com base no feedback dos clientes.

---

## Funcionalidades

- **Classificação de Reclamações**: Classifica automaticamente as reclamações em categorias predefinidas.
- **Resumos Automatizados**: Gera resumos das reclamações utilizando a API da OpenAI.
- **Agrupamento por Ocorrência**: Agrupa reclamações semelhantes para facilitar a análise.
- **Relatórios Consolidados**: Gera relatórios detalhados e consolidados com totais de tokens e custos.
- **Visualização de Dados**: Cria gráficos para análise visual das categorias de reclamações.

---

## Requisitos

- Python 3.9 ou superior
- Ambiente virtual (recomendado)
- API Key da OpenAI

---

## Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/reclameai.git
   cd reclameai 

2. **Crie e ative um ambiente virtual**:
   No Windows:
   ```bash
   python -m venv reclame_env
   reclame_env\Scripts\activate
   ```
   No Linux/Mac:
   ```bash
   python3 -m venv reclame_env
   source reclame_env/bin/activate
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure a API Key da OpenAI**:
   Crie um arquivo `.env` na raiz do projeto e adicione sua chave de API:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

---

## Como Rodar o Projeto

1. **Inicialize o ambiente do Kedro**:
   ```bash
   kedro install
   ```

2. **Execute o pipeline completo**:
   ```bash
   kedro run
   ```

3. **Visualize o pipeline (opcional)**:
   Para visualizar o pipeline no navegador, execute:
   ```bash
   kedro viz
   ```

---

## Estrutura do Projeto

A estrutura do projeto segue o padrão do Kedro:

```
reclameai/
├── conf/                   # Configurações do projeto
│   ├── base/               # Configurações padrão
│   └── local/              # Configurações locais (não versionadas)
├── data/                   # Dados de entrada e saída
│   ├── 01_raw/             # Dados brutos
│   ├── 02_intermediate/    # Dados intermediários
│   ├── 03_primary/         # Dados processados
│   ├── 04_feature/         # Dados prontos para análise
│   └── 08_reporting/       # Relatórios gerados
├── notebooks/              # Notebooks Jupyter para análise
├── src/                    # Código-fonte do projeto
│   ├── reclameai/          # Pacote principal do projeto
│   └── tests/              # Testes automatizados
└── README.md               # Documentação do projeto
```

---

## Exemplos de Uso

### Classificação de Reclamações
O pipeline processa os dados brutos e classifica as reclamações em categorias predefinidas. Exemplo de saída:

```
Relato: "Não consigo acessar o aplicativo do banco."
Categoria: Problema no acesso ao app
Resumo: O cliente relatou dificuldades para acessar o aplicativo.
```

### Relatório Consolidado
Após a execução do pipeline, um relatório consolidado será gerado em `data/08_reporting/relatorio_consolidado.txt` com os totais de tokens e custos.

---

## Testes

Para executar os testes automatizados, use o comando:

```bash
pytest
```

## Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo `LICENSE` para mais informações.     
