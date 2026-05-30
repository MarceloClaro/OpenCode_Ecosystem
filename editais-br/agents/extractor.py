"""ExtractorAgent (Agente 1) — extrai requisitos estruturados de editais.

Usa DeepSeek API (OpenAI-compatible) para processar o texto bruto de um
edital e retornar um JSON com os 7 filtros de captação.
"""

import json
import logging
import re

from openai import OpenAI

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Você é um especialista em análise de editais de fomento no Brasil.

Analise o texto do edital abaixo e extraia as informações no formato JSON especificado.

Regras:
1. Se uma informação não estiver disponível, use null (não invente dados)
2. Valores monetários em reais (BRL)
3. Datas no formato YYYY-MM-DD
4. eixos_tematicos use a taxonomia: saude, educacao, meio_ambiente, tecnologia,
   agricultura, cultura, esporte, direitos_humanos, desenvolvimento_social,
   infraestrutura, energia, defesa, turismo, comercio_exterior, inovacao,
   ciencias_exatas, ciencias_humanas, ciencias_biologicas, engenharia, outro
5. perfil_elegivel use: osc, startup_early_stage, startup_growth, mpe, me,
   empresa_medio_porte, empresa_grande, ict, pesquisador_individual,
   pessoa_fisica, cooperativa, governo_estadual, governo_municipal, outro
6. status: inscricoes_abertas, em_breve, encerrado, fluxo_continuo, suspenso, cancelado
7. nivel_trl_min e nivel_trl_max: inteiros de 1 a 9 (Technology Readiness Level)
8. score_complexidade: inteiro de 1 (muito simples) a 5 (muito complexo)

Retorne APENAS o JSON, sem texto adicional.

Texto do edital:
{texto_edital}

JSON:"""


class ExtractorAgent(BaseAgent):
    """Agente de extração de requisitos de editais.

    Usa DeepSeek V4 Flash para processar o texto bruto e retornar
    um dicionário estruturado com os 7 filtros de captação.
    """

    model: str = "deepseek-v4-flash"
    api_key: str = ""

    def __init__(self, model: str = "deepseek-v4-flash", api_key: str = ""):
        self.model = model
        self.api_key = api_key

    def execute(self, input_data: str) -> dict:
        """Executa a extração de requisitos do texto do edital.

        Args:
            input_data: Texto bruto do edital.

        Returns:
            Dicionário com os campos estruturados do edital.
        """
        if not input_data.strip():
            return {"titulo": "Desconhecido", "error": "Texto vazio"}

        prompt = self._build_prompt(input_data)
        response_text = self._call_api(prompt)

        return self._parse_response(response_text)

    def _build_prompt(self, texto: str) -> str:
        """Constrói o prompt para o modelo."""
        return EXTRACTION_PROMPT.format(texto_edital=texto)

    def _call_api(self, prompt: str) -> str:
        """Chama a API DeepSeek e retorna o texto da resposta.

        Args:
            prompt: Prompt completo a ser enviado.

        Returns:
            Texto da resposta do modelo.
        """
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=4000,
        )

        return response.choices[0].message.content or ""

    def _parse_response(self, response_text: str) -> dict:
        """Converte a resposta da API em um dicionário Python.

        Args:
            response_text: Texto retornado pelo modelo.

        Returns:
            Dicionário com os campos extraídos.
        """
        # Tenta extrair JSON de blocos ```json ... ```
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response_text)
        if json_match:
            response_text = json_match.group(1)

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.warning("JSON inválido na resposta, retornando raw")
            return {
                "error": "Falha ao parsear JSON",
                "raw_text": response_text,
            }
