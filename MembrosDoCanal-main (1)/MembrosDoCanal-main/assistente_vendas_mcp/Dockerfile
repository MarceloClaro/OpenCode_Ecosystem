# Etapa 1: Build
FROM python:3.11-slim AS build

WORKDIR /app

# Copiar somente requirements primeiro
COPY requirements.txt .

# Atualizar apt e instalar git, necessário para instalar pacotes do GitHub
RUN apt-get update && apt-get install -y git

# Instalar dependências do projeto
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Etapa 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copiar bibliotecas Python e binários do build
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copiar o código do projeto
COPY . .

# Permitir execução do entrypoint
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Comando de inicialização
ENTRYPOINT ["./entrypoint.sh"]

