#!/usr/bin/env python3
"""
PixelRAG MCP Server
====================
MCP Server para integração do PixelRAG com o OpenCode Ecosystem.

Ferramentas disponíveis:
- pixelshot: Renderiza documentos (URLs, PDFs, HTML) como screenshots em tiles
- pixelrag_search: Busca visual no índice FAISS
- pixelrag_index: Indexa documentos no pipeline visual
- pixelrag_render_and_search: Renderiza e busca em uma única operação

Autor: Marcelo Claro (OpenCode Ecosystem)
Versão: 1.0.0
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

# Configuração do MCP
MCP_SERVER_NAME = "pixelrag"
MCP_SERVER_VERSION = "1.0.0"

# Diretório de trabalho do ecossistema
ECOSYSTEM_DIR = Path(os.environ.get(
    "OPENCODE_ECOSYSTEM_DIR",
    "/mnt/c/Users/marce/Documents/OpenCode_Ecosystem"
))

# Diretório de índices visuais
PIXELRAG_INDEX_DIR = ECOSYSTEM_DIR / "pixelrag-indexes"
PIXELRAG_INDEX_DIR.mkdir(parents=True, exist_ok=True)


class PixelRAGMCPServer:
    """Servidor MCP para PixelRAG."""

    def __init__(self):
        self.tools = {
            "pixelshot": self._pixelshot,
            "pixelrag_search": self._pixelrag_search,
            "pixelrag_index": self._pixelrag_index,
            "pixelrag_render_and_search": self._pixelrag_render_and_search,
            "pixelrag_status": self._pixelrag_status,
        }

    async def _pixelshot(self, args: dict) -> dict:
        """
        Renderiza documentos como screenshots em tiles.
        
        Args:
            input_paths: Lista de URLs ou caminhos de arquivos para renderizar
            output_dir: Diretório de saída (opcional)
            backend: Backend de renderização - 'cdp' ou 'playwright' (padrão: cdp)
            workers: Número de workers paralelos (padrão: 4)
            tile_height: Altura dos tiles em pixels (padrão: 512)
            quality: Qualidade JPEG (padrão: 85)
            viewport_width: Largura do viewport (padrão: 1280)
            dpi: DPI para PDFs (padrão: 150)
        
        Returns:
            dict com resultado da renderização
        """
        input_paths = args.get("input_paths", [])
        output_dir = args.get("output_dir", str(PIXELRAG_INDEX_DIR / "tiles"))
        backend = args.get("backend", "cdp")
        workers = args.get("workers", 4)
        tile_height = args.get("tile_height", 512)
        quality = args.get("quality", 85)
        viewport_width = args.get("viewport_width", 1280)
        dpi = args.get("dpi", 150)

        if not input_paths:
            return {"error": "input_paths é obrigatório"}

        # Criar diretório de saída
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Construir comando
        cmd = [
            "pixelshot",
            "--output", output_dir,
            "--backend", backend,
            "--workers", str(workers),
            "--tile-height", str(tile_height),
            "--quality", str(quality),
            "--viewport-width", str(viewport_width),
            "--dpi", str(dpi),
        ] + input_paths

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # Contar tiles gerados
                tiles = list(Path(output_dir).glob("**/*.jpg"))
                return {
                    "success": True,
                    "output_dir": output_dir,
                    "tiles_generated": len(tiles),
                    "tiles": [str(t) for t in tiles[:10]],  # Primeiros 10
                    "stdout": result.stdout[:500],
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr[:1000],
                    "stdout": result.stdout[:500],
                }
        except subprocess.TimeoutExpired:
            return {"error": "Timeout na renderização (300s)"}
        except Exception as e:
            return {"error": str(e)}

    async def _pixelrag_search(self, args: dict) -> dict:
        """
        Busca visual no índice FAISS.
        
        Args:
            query: Texto ou caminho de imagem para busca
            index_dir: Diretório do índice FAISS
            top_k: Número de resultados (padrão: 5)
            query_type: Tipo de query - 'text' ou 'image' (padrão: text)
        
        Returns:
            dict com resultados da busca
        """
        query = args.get("query", "")
        index_dir = args.get("index_dir", str(PIXELRAG_INDEX_DIR / "faiss"))
        top_k = args.get("top_k", 5)
        query_type = args.get("query_type", "text")

        if not query:
            return {"error": "query é obrigatória"}

        # Verificar se o índice existe
        index_path = Path(index_dir)
        if not index_path.exists():
            return {
                "error": f"Índice não encontrado em {index_dir}",
                "suggestion": "Execute pixelrag_index primeiro para criar o índice"
            }

        # Para busca via API, usar pixelrag serve
        # Por enquanto, retornar instruções
        return {
            "info": "Para busca visual, inicie o servidor pixelrag serve",
            "command": f"pixelrag serve --index-dir {index_dir} --port 8080",
            "query": query,
            "top_k": top_k,
            "query_type": query_type,
            "api_endpoint": "http://localhost:8080/search"
        }

    async def _pixelrag_index(self, args: dict) -> dict:
        """
        Indexa documentos no pipeline visual completo.
        
        Args:
            input_paths: Lista de URLs ou caminhos de arquivos
            index_name: Nome do índice (padrão: 'default')
            embed_model: Modelo de embedding (padrão: 'qwen3-vl')
            chunk_size: Tamanho dos chunks em tiles (padrão: 1)
        
        Returns:
            dict com resultado da indexação
        """
        input_paths = args.get("input_paths", [])
        index_name = args.get("index_name", "default")
        embed_model = args.get("embed_model", "qwen3-vl")
        chunk_size = args.get("chunk_size", 1)

        if not input_paths:
            return {"error": "input_paths é obrigatório"}

        index_dir = PIXELRAG_INDEX_DIR / index_name
        index_dir.mkdir(parents=True, exist_ok=True)

        # Passo 1: Renderizar tiles
        tiles_dir = index_dir / "tiles"
        render_result = await self._pixelshot({
            "input_paths": input_paths,
            "output_dir": str(tiles_dir),
        })

        if not render_result.get("success"):
            return {"error": "Falha na renderização", "details": render_result}

        # Passo 2: Embedding e indexação FAISS
        # Nota: requer pixelrag[embed] instalado
        try:
            cmd = [
                sys.executable, "-m", "pixelrag",
                "build-index",
                "--input-dir", str(tiles_dir),
                "--output-dir", str(index_dir / "faiss"),
                "--model", embed_model,
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "index_name": index_name,
                    "index_dir": str(index_dir / "faiss"),
                    "tiles_dir": str(tiles_dir),
                    "tiles_count": render_result.get("tiles_generated", 0),
                }
            else:
                return {
                    "partial_success": True,
                    "tiles_dir": str(tiles_dir),
                    "tiles_count": render_result.get("tiles_generated", 0),
                    "embed_error": result.stderr[:500],
                    "suggestion": "Execute manualmente: pixelrag build-index --input-dir {tiles_dir} --output-dir {index_dir}/faiss"
                }
        except Exception as e:
            return {
                "partial_success": True,
                "tiles_dir": str(tiles_dir),
                "tiles_count": render_result.get("tiles_generated", 0),
                "embed_error": str(e),
            }

    async def _pixelrag_render_and_search(self, args: dict) -> dict:
        """
        Renderiza documentos e busca em uma única operação (pipeline completo).
        
        Args:
            input_paths: Lista de URLs ou caminhos de arquivos
            query: Texto ou caminho de imagem para busca
            top_k: Número de resultados (padrão: 5)
        
        Returns:
            dict com resultados da busca visual
        """
        input_paths = args.get("input_paths", [])
        query = args.get("query", "")
        top_k = args.get("top_k", 5)

        if not input_paths or not query:
            return {"error": "input_paths e query são obrigatórios"}

        # Criar diretório temporário para esta operação
        with tempfile.TemporaryDirectory(prefix="pixelrag_") as tmpdir:
            # Renderizar
            render_result = await self._pixelshot({
                "input_paths": input_paths,
                "output_dir": tmpdir,
            })

            if not render_result.get("success"):
                return {"error": "Falha na renderização", "details": render_result}

            # Indexar
            index_result = await self._pixelrag_index({
                "input_paths": input_paths,
                "index_name": Path(tmpdir).name,
            })

            # Buscar
            search_result = await self._pixelrag_search({
                "query": query,
                "index_dir": index_result.get("index_dir", ""),
                "top_k": top_k,
            })

            return {
                "render": render_result,
                "index": index_result,
                "search": search_result,
            }

    async def _pixelrag_status(self, args: dict) -> dict:
        """
        Retorna o status do PixelRAG no ecossistema.
        
        Returns:
            dict com informações de status
        """
        # Verificar instalação
        try:
            result = subprocess.run(
                ["pixelshot", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            installed = result.returncode == 0
        except:
            installed = False

        # Listar índices existentes
        indexes = []
        if PIXELRAG_INDEX_DIR.exists():
            for idx in PIXELRAG_INDEX_DIR.iterdir():
                if idx.is_dir():
                    tiles = list(idx.glob("**/*.jpg"))
                    indexes.append({
                        "name": idx.name,
                        "path": str(idx),
                        "tiles": len(tiles),
                    })

        return {
            "installed": installed,
            "version": "0.2.1",
            "index_dir": str(PIXELRAG_INDEX_DIR),
            "indexes": indexes,
            "tools": list(self.tools.keys()),
        }


# Instância global do servidor
server = PixelRAGMCPServer()


async def handle_request(request: dict) -> dict:
    """Processa uma requisição MCP."""
    method = request.get("method", "")
    params = request.get("params", {})

    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": name,
                    "description": func.__doc__.split("\n\n")[0] if func.__doc__ else "",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                    }
                }
                for name, func in server.tools.items()
            ]
        }
    
    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        if tool_name in server.tools:
            result = await server.tools[tool_name](arguments)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2, ensure_ascii=False)
                    }
                ]
            }
        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Ferramenta não encontrada: {tool_name}"
                }
            }
    
    elif method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": MCP_SERVER_NAME,
                "version": MCP_SERVER_VERSION,
            }
        }
    
    else:
        return {
            "error": {
                "code": -32601,
                "message": f"Método não suportado: {method}"
            }
        }


async def main():
    """Loop principal do servidor MCP (stdio)."""
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            if not line:
                break
            
            request = json.loads(line.strip())
            response = await handle_request(request)
            
            # Enviar resposta
            output = json.dumps(response)
            sys.stdout.write(f"{output}\n")
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except EOFError:
            break
        except Exception as e:
            error_response = {
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            sys.stdout.write(f"{json.dumps(error_response)}\n")
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
