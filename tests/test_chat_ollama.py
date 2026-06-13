"""TDD Tests for OpenCode Local RAG Chat & Vocalizer System."""

import os
import sys
import tempfile
import pytest

# Insere o diretório scripts no path para importar chat_ollama
scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
sys.path.insert(0, scripts_dir)

import chat_ollama


class TestChatOllama:
    """Testes unitários e de integração para chat_ollama.py."""

    def setup_method(self):
        # Cria arquivos temporários para teste sem afetar o ambiente real
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cmd_file = os.path.join(self.temp_dir.name, ".vocalizer_cmd")
        self.audit_log = os.path.join(self.temp_dir.name, "session_token_audit.log")
        
        # Patch nos caminhos de arquivo do chat_ollama
        self.orig_cmd_file = chat_ollama.CMD_FILE
        self.orig_audit_log = chat_ollama.AUDIT_LOG_PATH
        chat_ollama.CMD_FILE = self.cmd_file
        chat_ollama.AUDIT_LOG_PATH = self.audit_log

    def teardown_method(self):
        # Restaura os caminhos originais e limpa temporários
        chat_ollama.CMD_FILE = self.orig_cmd_file
        chat_ollama.AUDIT_LOG_PATH = self.orig_audit_log
        self.temp_dir.cleanup()

    def test_vocalizer_cmd_creation(self):
        """Verifica se falar() cria corretamente o comando de vocalização."""
        test_message = "Olá, bem-vindo ao ecossistema."
        chat_ollama.falar(test_message)
        
        assert os.path.exists(self.cmd_file)
        with open(self.cmd_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        # O comando deve começar com PLAY: e conter a mensagem limpa
        assert content.startswith("PLAY:")
        assert "Olá, bem-vindo ao ecossistema." in content

    def test_audit_log_save_and_load(self):
        """Testa o salvamento e recarregamento dos dados de tokenização acumulados."""
        # Valores de teste
        prompt_tokens = 500
        eval_tokens = 300
        savings = 0.000255
        
        chat_ollama.salvar_acumulado(prompt_tokens, eval_tokens, savings)
        
        assert os.path.exists(self.audit_log)
        
        # Recarrega e verifica se os valores batem
        loaded_prompt, loaded_eval, loaded_savings = chat_ollama.carregar_acumulado()
        
        assert loaded_prompt == prompt_tokens
        assert loaded_eval == eval_tokens
        assert pytest.approx(loaded_savings, abs=1e-6) == savings

    def test_load_empty_audit_log(self):
        """Verifica se carregar_acumulado() inicializa corretamente se o arquivo não existir."""
        if os.path.exists(self.audit_log):
            os.remove(self.audit_log)
            
        loaded_prompt, loaded_eval, loaded_savings = chat_ollama.carregar_acumulado()
        
        assert loaded_prompt == 0
        assert loaded_eval == 0
        assert loaded_savings == 0.0

    def test_clean_message_formatting(self):
        """Testa a higienização do texto para vocalização (removendo aspas e quebras)."""
        dirty_message = "Mensagem com \"aspas duplas\", 'simples' e\numa nova linha."
        chat_ollama.falar(dirty_message)
        
        with open(self.cmd_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        assert '"' not in content
        assert "'" not in content
        assert "\n" not in content
        assert "PLAY:Mensagem com aspas duplas, simples e uma nova linha." in content
