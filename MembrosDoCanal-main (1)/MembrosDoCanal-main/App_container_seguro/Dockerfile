# 1. Imagem base oficial + tag exata
FROM python:3.11.9-alpine3.19

# 2. Metadados da imagem
LABEL maintainer='dev@empresa.com'
LABEL version='1.0'

# 3. Criar usuário sem privilégios
RUN addgroup -S appgroup && \
    adduser -S appuser -G appgroup

WORKDIR /app

# 4. Copiar deps primeiro (cache)
COPY --chown=appuser:appgroup requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar código e ajustar dono
COPY --chown=appuser:appgroup . .

# 6. Expor porta sem publicar
EXPOSE 8000

# 7. Rodar como usuário não-root
USER appuser

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
