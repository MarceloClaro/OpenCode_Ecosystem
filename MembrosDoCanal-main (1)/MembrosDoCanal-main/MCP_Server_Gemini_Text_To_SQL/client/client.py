import asyncio
import sys
import json # ### MUDANÇA GROQ ### (Necessário para parsear argumentos da ferramenta)
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack


# Importações do MCP Client SDK (sem alteração)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ### MUDANÇA GROQ ### - Importar cliente Groq e possíveis erros
from groq import Groq, APIError, RateLimitError

from dotenv import load_dotenv

# Carrega variáveis de ambiente (agora buscando GROQ_API_KEY)
load_dotenv()

# ### MUDANÇA GROQ ### - Definir o modelo a ser usado

GROQ_MODEL_NAME = "llama-3.3-70b-versatile"

class MCPClient:
    """
    Cliente MCP para interagir com um servidor MCP via stdio e usar
    um modelo LLM via API Groq para processar consultas e utilizar
    as ferramentas do servidor.
    """
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        # ### MUDANÇA GROQ ### - Inicializar cliente Groq
        try:
            self.groq = Groq(api_key="")
        except Exception as e:
            print(f"Erro ao inicializar cliente Groq. Verifique sua GROQ_API_KEY no .env: {e}")
            sys.exit(1)

        self.stdio = None
        self.write = None

    # --- connect_to_server (Sem alterações significativas) ---
    async def connect_to_server(self, server_script_path: str):
        print(f"Tentando conectar ao servidor: {server_script_path}")
        is_python = server_script_path.endswith('.py')
        if not is_python:
            raise ValueError("O script do servidor deve ser um arquivo .py para este exemplo.")

        command = "python"
        server_params = StdioServerParameters(command=command, args=[server_script_path], env=None)
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        print("Sessão MCP inicializada.")
        response = await self.session.list_tools()
        tools = response.tools
        print("Conectado ao servidor com as seguintes ferramentas:", [tool.name for tool in tools])


    # --- process_query (Grandes alterações para Groq) ---
    async def process_query(self, query: str) -> str:
        if not self.session:
            return "Erro: Não conectado a um servidor MCP."

        print(f"\nProcessando consulta: '{query}'")

        messages: List[Dict[str, Any]] = [{"role": "user", "content": query}]

        # ### MUDANÇA GROQ ### - Formatar ferramentas para a API Groq/OpenAI
        mcp_tools_response = await self.session.list_tools()
        groq_tools = []
        tool_map = {} # Mapeia nome da ferramenta para descrição/schema original, se necessário
        for tool in mcp_tools_response.tools:
            tool_map[tool.name] = tool # Guardar info original se precisar depois
            # Groq/OpenAI esperam 'type' e 'function' com 'parameters' (JSON Schema)
            groq_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema # MCP SDK já fornece no formato JSON Schema
                }
            })

        print(f"Usando modelo Groq: {GROQ_MODEL_NAME}")
        print(f"Enviando consulta inicial para Groq com {len(groq_tools)} ferramentas...")

        try:          
            chat_completion = self.groq.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
            )

            response_message = chat_completion.choices[0].message

            # ### MUDANÇA GROQ ### - Loop para lidar com chamadas de ferramenta (tool_calls)
            while hasattr(response_message, 'tool_calls') and response_message.tool_calls:
                print(f"Groq solicitou o uso de ferramentas: {[tc.function.name for tc in response_message.tool_calls]}")

                # Adiciona a resposta do assistente (que contém os tool_calls) ao histórico
                # É importante fazer isso ANTES de adicionar os resultados das ferramentas
                messages.append({
                    "role": response_message.role, # Geralmente 'assistant'
                    "content": response_message.content, # Pode ser None
                    "tool_calls": [ # Formato esperado pela API Groq/OpenAI
                        {
                           "id": tc.id,
                           "type": tc.type, # 'function'
                           "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                        } for tc in response_message.tool_calls
                    ]
                 })


                tool_results_content = [] # Coleta resultados para a próxima chamada

                # Executa cada chamada de ferramenta solicitada
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    tool_call_id = tool_call.id
                    try:
                        # Argumentos vêm como string JSON, precisam ser parseados
                        function_args = json.loads(tool_call.function.arguments)
                        print(f"  Executando ferramenta '{function_name}' com args: {function_args}")

                        # Chama a ferramenta no servidor MCP
                        tool_result = await self.session.call_tool(function_name, function_args)
                        result_content = tool_result.content
                        print(f"  Resultado da ferramenta '{function_name}':\n{result_content}")

                        # Prepara o resultado para enviar de volta ao Groq
                        tool_results_content.append({
                                "tool_call_id": tool_call_id,
                                "role": "tool",
                                "name": function_name,
                                "content": result_content,
                        })

                    except json.JSONDecodeError as json_err:
                         print(f"  Erro ao decodificar argumentos JSON para '{function_name}': {json_err}")
                         print(f"  Argumentos recebidos: {tool_call.function.arguments}")
                         tool_results_content.append({
                             "tool_call_id": tool_call_id,
                             "role": "tool",
                             "name": function_name,
                             "content": f"Erro interno: Falha ao decodificar argumentos JSON - {json_err}",
                         })
                    except Exception as tool_err:
                        print(f"  Erro ao chamar/executar ferramenta '{function_name}' via MCP: {tool_err}")
                        tool_results_content.append({
                            "tool_call_id": tool_call_id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"Erro ao executar a ferramenta no servidor: {tool_err}",
                         })

                # Adiciona todos os resultados das ferramentas como uma única mensagem 'tool'
                messages.append({
                    "role": "tool",
                    "content": "\n".join([res["content"] for res in tool_results_content]) # Simplificado, API espera lista de blocos
                })
                # A API Groq/OpenAI espera uma mensagem por resultado de ferramenta, na verdade.
                # Vamos corrigir isso:
                messages.pop() # Remove a mensagem 'tool' agregada
                for res in tool_results_content:
                     messages.append({
                          "role": "tool",
                          "tool_call_id": res["tool_call_id"],
                          "name": res["name"], # Nome não é estritamente necessário aqui, mas pode ajudar
                          "content": res["content"]
                     })


                print("Enviando resultados da(s) ferramenta(s) de volta para Groq...")
                # Faz a próxima chamada para Groq com o histórico atualizado
                

                chat_completion = self.groq.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile",
                )

                response_message = chat_completion.choices[0].message
                # O loop continua se a nova resposta também pedir ferramentas

            # Fim do loop while: Nenhuma ferramenta mais solicitada, ou erro.
            final_response_content = response_message.content
            print(f"Resposta final do Groq (sem mais ferramentas): '{final_response_content}'")

            # Retorna o conteúdo final da resposta do assistente
            return final_response_content if final_response_content else "[O assistente não forneceu texto final após as ferramentas.]"

        # ### MUDANÇA GROQ ### - Capturar erros específicos da API Groq
        except RateLimitError:
            print("Erro: Limite de taxa da API Groq atingido. Tente novamente mais tarde.")
            return "Desculpe, estou recebendo muitas requisições no momento. Tente novamente em breve."
        except APIError as e:
            print(f"Erro na API Groq: {e.status_code} - {e.message}")
            return f"Desculpe, ocorreu um erro ao me comunicar com o serviço de IA: {e.message}"
        except json.JSONDecodeError as e:
             print(f"Erro ao decodificar resposta ou argumentos JSON: {e}")
             return f"Erro interno ao processar dados: {e}"
        except Exception as e:
            print(f"Erro inesperado durante processamento da query com Groq: {e}")
            # import traceback # Descomente para depuração
            # traceback.print_exc() # Descomente para depuração
            return f"Ocorreu um erro inesperado: {e}"

    # --- chat_loop (Sem alterações) ---
    async def chat_loop(self):
        print("\n Cliente MCP Iniciado! (Usando Groq)")
        print(f"Modelo: {GROQ_MODEL_NAME}")
        print("Digite suas consultas sobre produtos (ex: 'Quais camisetas custam menos de 25?')")
        print("Digite 'quit' para sair.")

        while True:
            try:
                query = input("\nVocê: ").strip()
                if query.lower() == 'quit':
                    print("Saindo...")
                    break
                if not query:
                    continue
                response_text = await self.process_query(query)
                print("\nLLM (Groq):", response_text) # ### MUDANÇA GROQ ### - Label opcional

            except KeyboardInterrupt:
                print("\nSaindo...")
                break
            except Exception as e:
                print(f"\nOcorreu um erro inesperado no chat: {str(e)}")

    # --- cleanup (Sem alterações) ---
    async def cleanup(self):
        print("\nLimpando recursos...")
        if self.session and not self.session.closed:
             try:
                 await self.session.close()
                 print("Sessão MCP fechada.")
             except Exception as e:
                 print(f"Erro ao fechar a sessão MCP: {e}")
        await self.exit_stack.aclose()
        print("Recursos limpos.")

# --- main (Sem alterações) ---
async def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <caminho_para_o_script_do_servidor.py>")
        print(f"Exemplo: python {sys.argv[0]} product_server.py")
        sys.exit(1)

    server_script_path = sys.argv[1]
    client = MCPClient()
    try:
        await client.connect_to_server(server_script_path)
        await client.chat_loop()
    except FileNotFoundError:
         print(f"Erro: O script do servidor não foi encontrado em '{server_script_path}'. Verifique o caminho.")
    except ValueError as ve:
         print(f"Erro de configuração: {ve}")
    except Exception as e:
        print(f"Erro crítico durante a execução: {e}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
