module.exports = {
  apps: [
    {
      name: "mirofish-server",
      script: "skills/mirofish-server/scripts/mirofish_server.py",
      interpreter: "python",
      args: "--port 8765",
      autorestart: true,
      watch: false,
      env: {
        PYTHONUNBUFFERED: "1"
      }
    },
    {
      name: "opencode-dashboard",
      script: "nexus/dashboard_server.py",
      interpreter: "python",
      args: "--porta 8081",
      autorestart: true,
      watch: false,
      env: {
        PYTHONUNBUFFERED: "1"
      }
    },
    {
      name: "self-healer",
      script: "nexus/self_healer.py",
      interpreter: "python",
      args: "--auto",
      autorestart: true,
      restart_delay: 300000, // Intervalo de 5 minutos entre execuções
      watch: false,
      env: {
        PYTHONUNBUFFERED: "1"
      }
    },
    {
      name: "evolution-loop",
      script: "nexus/evolution_loop.py",
      interpreter: "python",
      args: "--run-cycle",
      autorestart: true,
      restart_delay: 600000, // Intervalo de 10 minutos entre execuções
      watch: false,
      env: {
        PYTHONUNBUFFERED: "1"
      }
    }
  ]
};
