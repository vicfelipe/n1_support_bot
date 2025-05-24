FROM node:16-alpine

WORKDIR /app

# Copiar arquivos de configuração
COPY package.json package-lock.json* ./

# Instalar dependências
RUN npm install

# Copiar código fonte
COPY . .

# Expor porta
EXPOSE 3000

# Iniciar aplicação em modo de desenvolvimento
CMD ["npm", "start"]