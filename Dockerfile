FROM python:3.12-slim

LABEL org.opencontainers.image.title="OpenCode Ecosystem"
LABEL org.opencontainers.image.description="Plataforma IA multiagente com validacao CORA-Eval"
LABEL org.opencontainers.image.version="4.7.1"

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-lang-portuguese \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt 2>/dev/null || true
RUN pip install --no-cache-dir pytest numpy scipy

WORKDIR /app
COPY . .

RUN mkdir -p artigo/evaluations/tests/reports artigo/tests/reports

CMD ["python", "-m", "pytest", "artigo/evaluations/tests/", "-v", "--tb=short", "--timeout=300"]
