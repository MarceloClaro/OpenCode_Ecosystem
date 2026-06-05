import { useEffect, useRef, useCallback, useState } from "react";
import { io, Socket } from "socket.io-client";

export interface WebSocketMessage {
  type: string;
  message: string;
  severity?: "info" | "warning" | "error" | "success";
  data?: Record<string, any>;
  timestamp?: string;
}

export interface Alert {
  id?: number;
  type: "performance_degradation" | "retrain_recommended" | "error";
  message: string;
  severity: "low" | "medium" | "high";
  data?: Record<string, any>;
  is_read: boolean;
  timestamp?: string;
}

export function useWebSocket() {
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [notifications, setNotifications] = useState<WebSocketMessage[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [statistics, setStatistics] = useState<Record<string, any>>({});

  useEffect(() => {
    // Conectar ao servidor WebSocket
    const socket = io(window.location.origin, {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
    });

    socketRef.current = socket;

    // Eventos de conexão
    socket.on("connect", () => {
      console.log("✓ Conectado ao servidor WebSocket");
      setIsConnected(true);

      // Solicitar alertas não lidos
      socket.emit("get-unread-alerts");
    });

    socket.on("disconnect", () => {
      console.log("✗ Desconectado do servidor WebSocket");
      setIsConnected(false);
    });

    // Eventos de notificação
    socket.on("notification", (notification: WebSocketMessage) => {
      console.log("📢 Notificação recebida:", notification);
      setNotifications((prev) => [notification, ...prev.slice(0, 9)]);
    });

    // Eventos de alerta
    socket.on("alert", (alert: Alert) => {
      console.log("⚠️ Alerta recebido:", alert);
      setAlerts((prev) => [alert, ...prev]);
    });

    socket.on("unread-alerts", (unreadAlerts: Alert[]) => {
      console.log("📋 Alertas não lidos:", unreadAlerts);
      setAlerts(unreadAlerts);
    });

    // Eventos de análise
    socket.on("analysis-completed", (data) => {
      console.log("✓ Análise concluída:", data);
      setNotifications((prev) => [
        {
          type: "analysis",
          message: `Análise concluída: ${data.analysis.predicted_class}`,
          severity: "success",
          data,
          timestamp: data.timestamp,
        },
        ...prev.slice(0, 9),
      ]);
    });

    // Eventos de feedback
    socket.on("feedback-received", (data) => {
      console.log("✓ Feedback recebido:", data);
      const message = data.wasCorrect
        ? `Feedback confirmado: ${data.feedback.correct_class}`
        : `Correção registrada: ${data.feedback.predicted_class} → ${data.feedback.correct_class}`;

      setNotifications((prev) => [
        {
          type: "feedback",
          message,
          severity: data.wasCorrect ? "success" : "warning",
          data,
          timestamp: data.timestamp,
        },
        ...prev.slice(0, 9),
      ]);
    });

    // Eventos de estatísticas
    socket.on("statistics-updated", (data) => {
      console.log("📊 Estatísticas atualizadas:", data);
      setStatistics(data);
    });

    // Eventos de erro
    socket.on("error", (error) => {
      console.error("❌ Erro do servidor:", error);
      setNotifications((prev) => [
        {
          type: "error",
          message: error.message || "Erro do servidor",
          severity: "error",
          data: error,
          timestamp: new Date().toISOString(),
        },
        ...prev.slice(0, 9),
      ]);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  // Funções para enviar eventos
  const sendAnalysis = useCallback((analysis: Record<string, any>) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit("new-analysis", analysis);
    }
  }, []);

  const sendFeedback = useCallback((feedback: Record<string, any>) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit("new-feedback", feedback);
    }
  }, []);

  const requestStatistics = useCallback(() => {
    if (socketRef.current?.connected) {
      socketRef.current.emit("request-statistics");
    }
  }, []);

  const markAlertAsRead = useCallback((alertId: number) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit("mark-alert-read", alertId);
      setAlerts((prev) =>
        prev.map((alert) =>
          alert.id === alertId ? { ...alert, is_read: true } : alert
        )
      );
    }
  }, []);

  const clearNotification = useCallback((index: number) => {
    setNotifications((prev) => prev.filter((_, i) => i !== index));
  }, []);

  return {
    isConnected,
    notifications,
    alerts,
    statistics,
    sendAnalysis,
    sendFeedback,
    requestStatistics,
    markAlertAsRead,
    clearNotification,
  };
}

export default useWebSocket;
