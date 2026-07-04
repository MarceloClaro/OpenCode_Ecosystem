"""
CLI unificada do ecossistema — parser argparse e dispatch.
"""

import argparse
import sys
from typing import NoReturn

from ecosystem import get_version


def build_parser() -> argparse.ArgumentParser:
    """Constrói o parser de argumentos da CLI."""
    parser = argparse.ArgumentParser(
        prog="ecosystem",
        description="OpenCode Ecosystem — CLI Canônica Unificada",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comandos disponíveis:
  menu       Menu adaptativo interativo
  status     Status resumido do ecossistema
  doctor     Diagnóstico completo de saúde
  run        Executa um script no ecossistema
  serve      Inicia um servidor (dashboard, api, mcp)
  sync       Sincronização do ecossistema
  evolve     Ciclo evolutivo
  audit      Auditoria completa
  test       Executa suítes de teste
  help       Ajuda detalhada

Plugins:
  --list-plugins   Lista plugins registrados dinamicamente

Use 'ecosystem <comando> --help' para ajuda específica.
        """,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"OpenCode Ecosystem {get_version()}",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Modo verboso (saída detalhada)",
    )
    parser.add_argument(
        "--list-plugins",
        action="store_true",
        help="Lista plugins registrados no ecossistema",
    )

    # Subcomandos
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # menu
    p_menu = subparsers.add_parser("menu", help="Menu adaptativo interativo")

    # status
    p_status = subparsers.add_parser("status", help="Status resumido do ecossistema")
    p_status.add_argument("--json", action="store_true", help="Saída em JSON")

    # doctor
    p_doctor = subparsers.add_parser("doctor", help="Diagnóstico completo de saúde")
    p_doctor.add_argument("--fix", action="store_true", help="Tenta corrigir problemas automaticamente")

    # run
    p_run = subparsers.add_parser("run", help="Executa um script no ecossistema")
    p_run.add_argument("script", nargs="?", help="Nome do script ou caminho")
    p_run.add_argument("args", nargs=argparse.REMAINDER, help="Argumentos para o script")

    # serve
    p_serve = subparsers.add_parser("serve", help="Inicia um servidor")
    p_serve.add_argument("service", choices=["dashboard", "api", "mcp", "all"], help="Serviço a iniciar")
    p_serve.add_argument("--port", type=int, help="Porta do servidor")

    # sync
    p_sync = subparsers.add_parser("sync", help="Sincronização do ecossistema")
    p_sync.add_argument("--force", action="store_true", help="Força sincronização completa")

    # evolve
    p_evolve = subparsers.add_parser("evolve", help="Ciclo evolutivo")
    p_evolve.add_argument("--dry-run", action="store_true", help="Simula evolução sem aplicar")

    # audit
    p_audit = subparsers.add_parser("audit", help="Auditoria completa")
    p_audit.add_argument("--output", choices=["text", "json", "html"], default="text", help="Formato de saída")

    # test
    p_test = subparsers.add_parser("test", help="Executa suítes de teste")
    p_test.add_argument("--suite", help="Nome da suíte (ex: core, ecosystem, all)")
    p_test.add_argument("--verbose", action="store_true", help="Saída verbosa dos testes")

    return parser


def cmd_menu(args: argparse.Namespace) -> int:
    """Executa o menu adaptativo."""
    try:
        from menu import main as menu_main
        return menu_main()
    except ImportError as e:
        print(f"ERRO: Não foi possível carregar o menu: {e}", file=sys.stderr)
        return 1


def cmd_status(args: argparse.Namespace) -> int:
    """Exibe status resumido do ecossistema."""
    try:
        from ecosystem.status import show_status
        show_status(json_output=args.json)
        return 0
    except ImportError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1


def cmd_doctor(args: argparse.Namespace) -> int:
    """Executa diagnóstico de saúde."""
    try:
        from ecosystem.doctor import run_diagnosis
        return run_diagnosis(auto_fix=args.fix)
    except ImportError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1


def cmd_run(args: argparse.Namespace) -> int:
    """Executa um script."""
    from ecosystem.adapters.script_runner import run_script
    return run_script(args.script, args.args)


def cmd_serve(args: argparse.Namespace) -> int:
    """Inicia um servidor."""
    from ecosystem.adapters.server_launcher import launch_server
    return launch_server(args.service, port=args.port)


def cmd_sync(args: argparse.Namespace) -> int:
    """Executa sincronização."""
    from ecosystem.adapters.sync_runner import run_sync
    return run_sync(force=args.force)


def cmd_evolve(args: argparse.Namespace) -> int:
    """Executa ciclo evolutivo."""
    from ecosystem.adapters.evolve_runner import run_evolve
    return run_evolve(dry_run=args.dry_run)


def cmd_audit(args: argparse.Namespace) -> int:
    """Executa auditoria."""
    from ecosystem.adapters.audit_runner import run_audit
    return run_audit(output_format=args.output)


def cmd_test(args: argparse.Namespace) -> int:
    """Executa suítes de teste."""
    from ecosystem.adapters.test_runner import run_tests
    return run_tests(suite=args.suite, verbose=args.verbose)


def cmd_list_plugins() -> int:
    """Lista plugins registrados."""
    try:
        from ecosystem.plugin_discovery import list_plugins
        plugins = list_plugins()
        if not plugins:
            print("Nenhum plugin registrado.")
            return 0
        print(f"Plugins registrados ({len(plugins)}):")
        for p in plugins:
            print(f"  - {p['name']} v{p.get('version', '?')}: {p.get('description', '')}")
        return 0
    except ImportError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1


COMMAND_MAP = {
    "menu": cmd_menu,
    "status": cmd_status,
    "doctor": cmd_doctor,
    "run": cmd_run,
    "serve": cmd_serve,
    "sync": cmd_sync,
    "evolve": cmd_evolve,
    "audit": cmd_audit,
    "test": cmd_test,
}


def main(argv: list[str] | None = None) -> int:
    """Função principal da CLI.

    Returns:
        Código de saída (0 = sucesso, !=0 = erro)
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # Modo verboso
    if args.verbose:
        print(f"OpenCode Ecosystem {get_version()}", file=sys.stderr)

    # --list-plugins
    if args.list_plugins:
        return cmd_list_plugins()

    # Sem comando
    if not args.command:
        parser.print_help()
        return 0

    # Dispatch do comando
    handler = COMMAND_MAP.get(args.command)
    if handler:
        try:
            return handler(args)
        except Exception as e:
            print(f"ERRO ao executar comando '{args.command}': {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    else:
        print(f"Comando desconhecido: {args.command}", file=sys.stderr)
        print(f"Use 'ecosystem --help' para ver os comandos disponíveis.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
