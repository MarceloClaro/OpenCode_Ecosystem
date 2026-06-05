"""Testes do ExtractorAgent (Agente 1) — Issue #12."""

from unittest.mock import MagicMock, patch


def test_extractor_agent_existe_e_herda_base():
    """ExtractorAgent deve herdar de BaseAgent."""
    from agents.base import BaseAgent
    from agents.extractor import ExtractorAgent

    assert issubclass(ExtractorAgent, BaseAgent)


def test_extractor_agent_tem_model_e_api_key():
    """Deve aceitar model e api_key no construtor."""
    from agents.extractor import ExtractorAgent

    agent = ExtractorAgent(
        model="deepseek-v4-flash",
        api_key="sk-test",
    )
    assert agent.model == "deepseek-v4-flash"
    assert agent.api_key == "sk-test"


def test_execute_chama_api_com_prompt():
    """execute() deve chamar a API com o prompt de extração."""
    from agents.extractor import ExtractorAgent

    agent = ExtractorAgent(model="test", api_key="sk-test")

    with patch.object(agent, "_call_api") as mock_call:
        mock_call.return_value = '{"titulo": "Edital X", "resumo": "Teste"}'
        result = agent.execute("Texto do edital de fomento...")

    mock_call.assert_called_once()
    assert "titulo" in result
    assert result["titulo"] == "Edital X"


def test_execute_retorna_dict_mesmo_com_json_invalido():
    """Se API retornar JSON inválido, deve retornar dict com erro."""
    from agents.extractor import ExtractorAgent

    agent = ExtractorAgent(model="test", api_key="sk-test")

    with patch.object(agent, "_call_api") as mock_call:
        mock_call.return_value = "resposta não é json ```json...```"
        result = agent.execute("Texto qualquer")

    assert isinstance(result, dict)
    assert "error" in result or "raw_text" in result


def test_execute_com_texto_vazio():
    """Texto vazio não deve quebrar."""
    from agents.extractor import ExtractorAgent

    agent = ExtractorAgent(model="test", api_key="sk-test")

    with patch.object(agent, "_call_api") as mock_call:
        mock_call.return_value = '{"titulo": "Desconhecido"}'
        result = agent.execute("")

    assert isinstance(result, dict)


def test_prompt_contem_texto_do_edital():
    """O prompt deve conter o texto original do edital."""
    from agents.extractor import ExtractorAgent

    agent = ExtractorAgent(model="test", api_key="sk-test")
    texto = "CHAMADA PÚBLICA FAPEG 01/2026 - Fomento à pesquisa aplicada"

    prompt = agent._build_prompt(texto)
    assert "CHAMADA PÚBLICA" in prompt
    assert "FAPEG" in prompt
    assert "json" in prompt.lower()


def test_call_api_envia_para_deepseek():
    """_call_api deve enviar requisição para o endpoint correto."""
    from unittest.mock import patch

    from agents.extractor import ExtractorAgent

    agent = ExtractorAgent(model="deepseek-v4-flash", api_key="sk-test")

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"titulo": "X"}'

    with patch("agents.extractor.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        result = agent._call_api("prompt de teste")

    mock_openai.assert_called_once_with(
        api_key="sk-test",
        base_url="https://api.deepseek.com",
    )
    assert result == '{"titulo": "X"}'
