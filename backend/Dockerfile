FROM python:3.9-slim

WORKDIR /app

# Atualizar pip e instalar ferramentas essenciais
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .

# Instalar as demais dependências
RUN pip install -r requirements.txt

# Baixar modelo spaCy para português (modelo menor)
RUN python -m spacy download pt_core_news_sm || echo "Falha ao baixar modelo pt_core_news_sm, continuando mesmo assim"

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]