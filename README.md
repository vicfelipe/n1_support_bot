# Chatbot para Suporte N1 Integrado com OCOMON - Alpha Project

Este projeto implementa um chatbot para suporte de nível 1 (N1) integrado com o sistema OCOMON como base de conhecimento. O chatbot é capaz de buscar soluções na base de conhecimento do OCOMON e, caso não encontre uma solução, criar tickets automaticamente.

Futuramente a ideia é que seja um bot agnóstico a base de conhecimento do OCOMON, ou seja, pode ser usado com qualquer sistema de helpdesk.

## Arquitetura

O projeto está dividido em duas partes principais:

- **Backend**: Desenvolvido em Python, responsável pela lógica de negócio, integração com a API do OCOMON e processamento de linguagem natural.
- **Frontend**: Desenvolvido em React.js, fornece a interface de usuário para interação com o chatbot.

Ambas as partes são containerizadas usando Docker para facilitar a implantação e escalabilidade.

## Estrutura do Projeto

```
n1_support_bot/
├── .env                      # Variáveis de ambiente
├── docker-compose.yml        # Configuração dos containers
├── README.md                 # Documentação do projeto
├── backend/
│   ├── Dockerfile            # Configuração do container do backend
│   ├── requirements.txt      # Dependências Python
│   └── app/
│       ├── __init__.py
│       ├── main.py           # Aplicação FastAPI
│       ├── models/           # Modelos de dados
│       │   ├── __init__.py
│       │   ├── conversation.py
│       │   └── message.py
│       ├── services/         # Serviços de negócio
│       │   ├── __init__.py
│       │   ├── nlp_service.py    # Processamento de linguagem natural
│       │   └── ocomon_service.py # Integração com API OCOMON
│       └── utils/            # Utilitários
│           ├── __init__.py
│           └── database.py
└── frontend/
    ├── Dockerfile            # Configuração do container do frontend
    ├── package.json          # Dependências JavaScript
    ├── public/               # Arquivos públicos
    │   ├── index.html
    │   └── manifest.json
    └── src/                  # Código fonte React
        ├── App.css
        ├── App.js            # Componente principal
        ├── components/       # Componentes React
        │   ├── ChatInterface.jsx
        │   └── MessageBubble.jsx
        ├── index.css
        ├── index.js          # Ponto de entrada
        ├── reportWebVitals.js
        └── theme.js          # Configuração do tema Material-UI
```

## Fluxo da Aplicação

```
flowchart TD
    A[Usuário inicia conversa] --> B[Bot solicita detalhes]
    B --> C[Usuário descreve problema]
    C --> D[Busca na base OCOMON]
    D -->|Encontrou solução| E[Apresenta solução]
    D -->|Não encontrou| F[Cria ticket]
    E --> G[Pergunta se resolveu]
    G -->|Sim| H[Registra sucesso]
    G -->|Não| F
    F --> I[Informa número do ticket]
```

## Funcionalidades Implementadas

### Backend

1. **API RESTful com FastAPI**: Endpoints para chat e feedback
2. **Processamento de Linguagem Natural**: Utilizando spaCy para análise de intenções e entidades
3. **Integração com OCOMON**: Serviço para busca na base de conhecimento e criação de tickets
4. **Gestão de Conversas**: Modelo para armazenar e gerenciar conversas e mensagens

### Frontend

1. **Interface de Chat**: Interface amigável com Material-UI
2. **Componentes Reutilizáveis**: MessageBubble para exibição de mensagens
3. **Integração com Backend**: Comunicação via Axios
4. **Feedback de Usuário**: Suporte para confirmação de solução e abertura de tickets

## Configuração e Execução

### Pré-requisitos

- Docker e Docker Compose instalados
- Acesso à API do OCOMON

### Instalação

1. Clone o repositório
2. Configure as variáveis de ambiente no arquivo `.env`
3. Configure o arquivo docker-compose.yml
3. Execute `docker-compose up -d`
4. É necessário um container com o OCOMON, para isso, execute o comando:
`docker run -it -p 8080:80 3306:3306 flaviorib/ocomon:6.0"` 

### Acesso

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Container OCOMON: http://localhost:8080
- Banco de dados: localhost:3306

## Tecnologias Utilizadas

- **Backend**: 
  - Python 3.9
  - FastAPI para API RESTful
  - spaCy para processamento de linguagem natural
  - MySQL Connector para conexão com MariaDB
  - Pydantic para validação de dados

- **Frontend**: 
  - React.js 18
  - Material-UI para componentes de interface
  - Axios para requisições HTTP
  - React Router para navegação
  - React Markdown para renderização de conteúdo formatado

- **Infraestrutura**: 
  - Docker e Docker Compose
  - MariaDB 10.6

## Integração com OCOMON

A integração com o OCOMON é feita via API REST, utilizando os endpoints fornecidos pelo sistema:

- **Criação de Tickets**: `POST http://localhost:8080/api/ocomon_api/tickets/`
- **Consulta de Tickets**: `GET http://localhost:8080/api/ocomon_api/tickets/{número}`

## Melhorias Futuras

1. Implementar autenticação de usuários
2. Melhorar o modelo de NLP com treinamento específico para suporte técnico
3. Adicionar histórico de conversas persistente
4. Implementar análise de sentimento para detectar frustração do usuário
5. Adicionar integração com outros sistemas de helpdesk além do OCOMON