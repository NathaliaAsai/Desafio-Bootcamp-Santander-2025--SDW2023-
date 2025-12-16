**ETL com IA - Bootcamp Santander 2025 (Ciência de Dados com Python**
Este projeto foi desenvolvido como parte do desafio do Bootcamp Santander 2025 (Desafio Santander Dev Week 2023), com o objetivo de aplicar conceitos de ETL (Extraxt, Transform, Load) aliados ao uso de IA para geração de mensagens personalizadas.
A solução realiza a leitura de dados de usuários a partir de um arquivo CSV, classifica os usuários em diferentes segmentos e utiliza um modelo de linguagem (LLM) para criar mensagens personalizadas de acordo com o perfil de cada cliente.

**Funcionalidades**
- Leitura de dados de usuários a partir de arquivo CSV;
- Segmentação automática de usuários com base no saldo da conta;
- Geração de mensagens personalizadas utilizando IA (Hugging Face + Llama);
- Uso de fallback com mensagens fixas em caso de falha na geração por IA;
- Exportação do resultado final em formato JSON.

**Tecnologias Utilizadas**
- Python
- Pandas
- Hugging Face Hub
- Llama 3.2 Instruct (Together AI)
- dotenv
- Git & GitHub

**Estrutura do Projeto**
.
├── DesafioSDW2023.py
├── SDW2023.csv
├── .env.example
├── .gitignore
└── README.md

**PARA EXECUTAR O PROJETO3**
1) Acesse a pasta do projeto via terminal
2) Crie e ative um ambiente virtural
     python -m venv venv
     venv\Scripts\activate
3) Instale as dependencias
     pip install -r requirements.txt
4)Configure as variaveis de ambiente (crie um arquivo .env com os seguintes conteúdos):
      HF_API_ATOKEN=XXX-SEU-TOKEN-HUGGINGFACE-XXX
      HF_MODEL_ID==meta-llama/Llama-3.2-3B-Instruct:together
     #sim, precisa tere o together!
5) Execute o projeto via terminal
     python DesafioSDW2023.py

**Observação**
Este projeto foi desenvolvido com fins educacionais, como prática de integração entre engenharia de dados e inteligência artificial, simulando um cenário real de personalização de comunicação em instituições financeiras.

Foi utilizado o ChatGPT (OpenAI) como ferramenta de auxílio para esclarecimento de conceitos, depuração de código, ajustes de integração com APIs de IA e melhoria da organização e documentação do projeto.
