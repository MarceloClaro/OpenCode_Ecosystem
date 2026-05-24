#!/usr/bin/env python3
"""
WhatsApp Web Connector Service — Gera QR code, conecta WhatsApp Web,
baixa conversas de grupos e gera perfis cognitivos em tempo real.

Porta: 8766 (independente do MiroFish)
Dependência: playwright (pip install playwright && playwright install chromium)

Arquitetura:
  QR Code → Usuário escaneia → Conexão estabelecida → Download automático
  → WhatsAppProfiler gera perfis → SimAgents calibrados → Simulação refinada
"""

import http.server
import json
import os
import sys
import base64
import io
import time
import threading
import queue
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs

BRAZIL_TZ = timezone(timedelta(hours=-3))

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("[WARN] playwright nao instalado. Execute:")
    print("  pip install playwright")
    print("  playwright install chromium")

# ═══════════════════════════════════════════════════════════════════
# WhatsApp Web Controller
# ═══════════════════════════════════════════════════════════════════

class WhatsAppController:
    """Controla WhatsApp Web via Playwright."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.connected = False
        self.qr_code_base64: Optional[str] = None
        self.status: str = "offline"
        self.chats: List[Dict] = []
        self.chat_names: List[str] = []
        self._lock = threading.Lock()

    def start(self) -> bool:
        """Inicia navegador e navega para WhatsApp Web."""
        if not HAS_PLAYWRIGHT:
            self.status = "erro: playwright nao instalado"
            return False

        try:
            self.status = "iniciando navegador..."
            self.playwright = sync_playwright().start()

            # Tenta usar perfil existente para evitar re-scan
            user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "..", "..", "..", ".reversa", "whatsapp_profile")
            os.makedirs(user_data_dir, exist_ok=True)

            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,  # Precisa ser visível para o QR code
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 800, "height": 900},
            )

            if self.browser.pages:
                self.page = self.browser.pages[0]
            else:
                self.page = self.browser.new_page()

            self.status = "conectando ao WhatsApp Web..."
            self.page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=30000)

            # Verifica se já está logado
            time.sleep(3)
            self._check_connection()

            return True
        except Exception as e:
            self.status = f"erro ao iniciar: {str(e)[:100]}"
            return False

    def _check_connection(self):
        """Verifica se já está conectado ao WhatsApp Web."""
        try:
            # Se já conectado (perfil persistente), o QR não aparece
            qr_element = self.page.query_selector('canvas[aria-label="Scan me!"]')
            qr_element2 = self.page.query_selector('[data-testid="qrcode"]')
            search_box = self.page.query_selector('[data-testid="chat-list-search"]')
            chat_list = self.page.query_selector('[data-testid="chat-list"]')

            if chat_list and (search_box or not qr_element):
                self.connected = True
                self.status = "conectado"
                self.qr_code_base64 = None
                print("[WhatsApp] Ja conectado (perfil persistente)")
            elif qr_element or qr_element2:
                self.connected = False
                self.status = "aguardando scan do QR code"
                self._capture_qr()
                print("[WhatsApp] QR code gerado - aguardando scan")
            else:
                self.status = "carregando..."
                self.qr_code_base64 = None

        except Exception as e:
            self.status = f"verificando: {str(e)[:50]}"

    def _capture_qr(self):
        """Captura QR code da página."""
        try:
            # Tenta múltiplos seletores
            for selector in ['canvas[aria-label="Scan me!"]', '[data-testid="qrcode"]',
                            '[data-ref] canvas', 'div[data-ref] canvas']:
                qr = self.page.query_selector(selector)
                if qr:
                    screenshot = qr.screenshot()
                    self.qr_code_base64 = base64.b64encode(screenshot).decode()
                    return

            # Fallback: screenshot da página inteira recortado
            screenshot = self.page.screenshot()
            self.qr_code_base64 = base64.b64encode(screenshot).decode()
            self.status = "qr capturado (fallback)"
        except Exception as e:
            self.qr_code_base64 = None
            self.status = f"erro ao capturar QR: {str(e)[:50]}"

    def wait_for_connection(self, timeout_seconds: int = 120) -> bool:
        """Aguarda usuário escanear QR code."""
        if self.connected:
            return True

        start = time.time()
        self.status = "aguardando scan do QR code..."

        while time.time() - start < timeout_seconds:
            try:
                # Verifica se o chat list apareceu
                chat_list = self.page.query_selector('[data-testid="chat-list"]')
                if chat_list:
                    self.connected = True
                    self.status = "conectado"
                    self.qr_code_base64 = None
                    time.sleep(2)  # Aguarda carregar
                    return True

                # Verifica se QR ainda está visível (se sumiu = conectou)
                qr = self.page.query_selector('canvas[aria-label="Scan me!"]')
                if not qr:
                    time.sleep(2)
                    chat_list = self.page.query_selector('[data-testid="chat-list"]')
                    if chat_list:
                        self.connected = True
                        self.status = "conectado"
                        self.qr_code_base64 = None
                        return True

                time.sleep(1)
            except Exception:
                time.sleep(2)

        self.status = "timeout: QR nao escaneado"
        return False

    def fetch_chats(self, limit: int = 20) -> List[Dict]:
        """Baixa lista de conversas e mensagens recentes."""
        if not self.connected or not self.page:
            return []

        self.status = "baixando conversas..."
        chats = []

        try:
            # Clica em cada chat e extrai mensagens
            chat_items = self.page.query_selector_all('[data-testid="chat-list"] > div')
            self.chat_names = []

            for i, item in enumerate(chat_items[:limit]):
                try:
                    # Nome do chat
                    name_el = item.query_selector('[data-testid="cell-frame-title"]')
                    name = name_el.inner_text() if name_el else f"Chat_{i}"

                    # Última mensagem
                    last_msg_el = item.query_selector('[data-testid="last-msg-status"]')
                    last_msg = last_msg_el.inner_text() if last_msg_el else ""

                    self.chat_names.append(name)
                    chats.append({
                        "name": name,
                        "index": i,
                        "last_message": last_msg,
                        "type": "group" if "," in name or " " in name else "direct",
                    })

                    if len(chats) >= limit:
                        break
                except Exception:
                    continue

            self.chats = chats
            self.status = f"{len(chats)} conversas encontradas"
            return chats

        except Exception as e:
            self.status = f"erro ao baixar chats: {str(e)[:50]}"
            return []

    def fetch_messages(self, chat_index: int = 0, message_limit: int = 200) -> List[Dict]:
        """Baixa mensagens de uma conversa específica."""
        if not self.connected or not self.page:
            return []

        try:
            chat_items = self.page.query_selector_all('[data-testid="chat-list"] > div')
            if chat_index >= len(chat_items):
                return []

            # Clica no chat
            chat_items[chat_index].click()
            time.sleep(2)

            messages = []
            last_height = 0
            scroll_attempts = 0

            while len(messages) < message_limit and scroll_attempts < 10:
                # Extrai mensagens visíveis
                msg_elements = self.page.query_selector_all('[data-testid="msg-container"]')
                for el in msg_elements[len(messages):]:
                    try:
                        sender_el = el.query_selector('[data-testid="msg-meta"]')
                        sender = sender_el.inner_text() if sender_el else "?"

                        text_el = el.query_selector('[data-testid="msg-text"]')
                        text = text_el.inner_text() if text_el else ""

                        time_el = el.query_selector('[data-testid="msg-time"]')
                        msg_time = time_el.get_attribute("datetime") if time_el else ""

                        if text.strip():
                            messages.append({
                                "sender": sender,
                                "content": text,
                                "datetime": msg_time or datetime.now(BRAZIL_TZ).isoformat(),
                            })
                    except Exception:
                        continue

                # Scroll para cima
                scroll_attempts += 1
                self.page.evaluate("document.querySelector('[data-testid=\"conversation-panel-messages\"]').scrollTop = 0")
                time.sleep(1.5)

                # Verifica se scroll funcionou
                new_height = self.page.evaluate(
                    "document.querySelector('[data-testid=\"conversation-panel-messages\"]')?.scrollHeight || 0"
                )
                if new_height == last_height:
                    break
                last_height = new_height

            self.status = f"{len(messages)} mensagens baixadas"
            return messages[:message_limit]

        except Exception as e:
            self.status = f"erro ao baixar mensagens: {str(e)[:50]}"
            return []

    def stop(self):
        """Fecha navegador e libera recursos."""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
        self.connected = False
        self.status = "offline"


# ═══════════════════════════════════════════════════════════════════
# WhatsApp Service (HTTP + WebSocket-like polling)
# ═══════════════════════════════════════════════════════════════════

class WhatsAppServiceHandler(http.server.BaseHTTPRequestHandler):
    """Handler HTTP para o serviço WhatsApp."""

    controller: WhatsAppController = None

    def log_message(self, format, *args):
        pass

    def _send_json(self, data, status=200):
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
        except Exception:
            pass

    def _send_html(self, html, status=200):
        try:
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
        except Exception:
            pass

    def do_GET(self):
        path = self.path.split("?")[0]
        ctrl = self.controller

        if path == "/qr":
            if ctrl and ctrl.qr_code_base64:
                html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>WhatsApp QR</title>
<style>body{{background:#111;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;flex-direction:column;font-family:sans-serif}}
img{{border:3px solid #25D366;border-radius:16px;max-width:300px}}p{{color:#fff;margin-top:20px}}</style></head>
<body><img src="data:image/png;base64,{ctrl.qr_code_base64}"><p>📱 Escaneie o QR code com seu WhatsApp</p></body></html>"""
                self._send_html(html)
            elif ctrl and ctrl.connected:
                self._send_json({"status": "connected", "qr": None})
            else:
                self._send_json({"status": ctrl.status if ctrl else "offline", "qr": None})

        elif path == "/qr/raw":
            if ctrl and ctrl.qr_code_base64:
                self._send_json({"qr_base64": ctrl.qr_code_base64, "status": ctrl.status})
            else:
                self._send_json({"qr_base64": None, "status": ctrl.status if ctrl else "offline"})

        elif path == "/status":
            self._send_json({
                "connected": ctrl.connected if ctrl else False,
                "status": ctrl.status if ctrl else "offline",
                "chat_count": len(ctrl.chats) if ctrl else 0,
                "chat_names": ctrl.chat_names if ctrl else [],
                "has_qr": bool(ctrl.qr_code_base64) if ctrl else False,
            })

        elif path == "/chats":
            if not ctrl or not ctrl.connected:
                self._send_json({"error": "Nao conectado"}, 400)
                return
            self._send_json({"chats": ctrl.chats})

        elif path == "/health":
            self._send_json({
                "service": "whatsapp-connector",
                "playwright_available": HAS_PLAYWRIGHT,
                "controller_status": ctrl.status if ctrl else "not_started",
            })

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        path = self.path.split("?")[0]

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode() if length > 0 else "{}"
            params = json.loads(body) if body else {}
        except Exception:
            params = {}

        ctrl = self.controller

        if path == "/connect":
            # Controller ja foi iniciado em start_service()
            # Apenas retorna status atual — nao recria
            if ctrl:
                self._send_json({
                    "status": ctrl.status,
                    "has_qr": bool(ctrl.qr_code_base64),
                    "connected": ctrl.connected,
                })
            else:
                self._send_json({"status": "controller_nao_iniciado", "connected": False})

        elif path == "/messages":
            chat_idx = params.get("chat_index", 0)
            limit = params.get("limit", 200)
            if not ctrl or not ctrl.connected:
                self._send_json({"error": "Nao conectado"}, 400)
                return
            msgs = ctrl.fetch_messages(chat_idx, limit)
            self._send_json({"messages": msgs, "count": len(msgs)})

        elif path == "/disconnect":
            if ctrl:
                ctrl.stop()
                self.controller = None
            self._send_json({"status": "disconnected"})

        elif path == "/profiles":
            """Gera perfis cognitivos das conversas baixadas."""
            if not ctrl or not ctrl.connected:
                self._send_json({"error": "Nao conectado"}, 400)
                return

            chat_idx = params.get("chat_index", 0)
            msgs = ctrl.fetch_messages(chat_idx, 300)

            if not msgs:
                self._send_json({"error": "Nenhuma mensagem encontrada"}, 404)
                return

            # Usa WhatsAppProfiler
            try:
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
                from whatsapp_profiler import WhatsAppProfiler

                profiler = WhatsAppProfiler()
                profiler.parse_json(msgs)
                profiles = profiler.build_profiles()
                sim_agents = profiler.to_sim_agents()

                self._send_json({
                    "profiles": profiles,
                    "sim_agents": sim_agents,
                    "group_stats": profiler.group_stats,
                    "message_count": len(msgs),
                    "profile_count": len(profiles),
                })
            except Exception as e:
                self._send_json({"error": f"Erro ao gerar perfis: {str(e)}"}, 500)

        elif path == "/calibrate":
            """Envia perfis para calibrar simulação no MiroFish."""
            if not ctrl or not ctrl.connected:
                self._send_json({"error": "Nao conectado"}, 400)
                return

            chat_idx = params.get("chat_index", 0)
            msgs = ctrl.fetch_messages(chat_idx, 300)

            if not msgs:
                self._send_json({"error": "Nenhuma mensagem"}, 404)
                return

            try:
                from whatsapp_profiler import WhatsAppProfiler
                profiler = WhatsAppProfiler()
                profiler.parse_json(msgs)
                profiles = profiler.build_profiles()
                sim_agents = profiler.to_sim_agents()

                # Salva para o MiroFish server ler
                calib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "..", "..", "..", ".reversa", "whatsapp_calibration.json")
                os.makedirs(os.path.dirname(calib_path), exist_ok=True)
                with open(calib_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "calibrated_at": datetime.now(BRAZIL_TZ).isoformat(),
                        "profiles": profiles,
                        "sim_agents": sim_agents,
                        "group_stats": profiler.group_stats,
                    }, f, indent=2, ensure_ascii=False)

                self._send_json({
                    "status": "calibrated",
                    "agent_count": len(sim_agents),
                    "calibration_file": calib_path,
                    "message": f"{len(sim_agents)} agentes calibrados. Reinicie a simulacao."
                })
            except Exception as e:
                self._send_json({"error": f"Erro: {str(e)}"}, 500)

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def start_service(port: int = 8766):
    """Inicia o serviço WhatsApp Web em porta separada."""
    print("=" * 60)
    print("[WA] WHATSAPP WEB CONNECTOR SERVICE")
    print("=" * 60)
    print(f"   Porta: {port}")
    print(f"   QR Code: http://localhost:{port}/qr")
    print(f"   Status:  http://localhost:{port}/status")
    print(f"   API:     http://localhost:{port}/connect (POST)")
    print(f"   Perfis:  http://localhost:{port}/profiles (POST)")
    print(f"   Calibrar: http://localhost:{port}/calibrate (POST)")
    print("=" * 60)

    if not HAS_PLAYWRIGHT:
        print("\n[!] Playwright nao instalado!")
        print("   pip install playwright")
        print("   playwright install chromium")
        print("\n   O servico sera iniciado sem capacidade de conexao.")
        print("   Use WhatsAppProfiler com arquivos .txt exportados como fallback.")

    server = http.server.HTTPServer(("0.0.0.0", port), WhatsAppServiceHandler)

    # Iniciar controller
    controller = WhatsAppController()
    WhatsAppServiceHandler.controller = controller

    if HAS_PLAYWRIGHT:
        ok = controller.start()
        if ok:
            pass  # Frontend polls /qr/raw — sem Thread (greenlet conflict)

    print(f"\n   Servidor rodando em http://localhost:{port}")
    print(f"   Pressione Ctrl+C para parar\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n   Encerrando...")
        controller.stop()
        server.shutdown()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="WhatsApp Web Connector Service")
    parser.add_argument("--port", type=int, default=8766, help="Porta do serviço")
    parser.add_argument("--no-auto-start", action="store_true", help="Não iniciar WhatsApp automaticamente")
    args = parser.parse_args()

    start_service(args.port)
