import { Server as SocketIOServer } from "socket.io";
import { Server as HTTPServer } from "http";
import {
  saveFeedback,
  saveAnalysis,
  getClassStatistics,
  getGlobalStatistics,
  createAlert,
  getAlerts,
  markAlertAsRead,
  FeedbackRecord,
  AnalysisRecord,
  Alert,
} from "./database.js";

export interface ClientMetrics {
  clientId: string;
  lastAnalysisTime: number;
  analysisCount: number;
  avgConfidence: number;
}

export class WebSocketManager {
  private io: SocketIOServer;
  private clients: Map<string, ClientMetrics> = new Map();
  private performanceThreshold = 0.85; // Acurácia mínima aceitável

  constructor(httpServer: HTTPServer) {
    this.io = new SocketIOServer(httpServer, {
      cors: {
        origin: "*",
        methods: ["GET", "POST"],
      },
    });

    this.setupEventHandlers();
  }

  private setupEventHandlers() {
    this.io.on("connection", (socket) => {
      console.log(`✓ Cliente conectado: ${socket.id}`);

      // Registrar cliente
      this.clients.set(socket.id, {
        clientId: socket.id,
        lastAnalysisTime: Date.now(),
        analysisCount: 0,
        avgConfidence: 0,
      });

      // Enviar alertas não lidos
      socket.on("get-unread-alerts", async () => {
        const alerts = await getAlerts(true);
        socket.emit("unread-alerts", alerts);
      });

      // Marcar alerta como lido
      socket.on("mark-alert-read", async (alertId: number) => {
        await markAlertAsRead(alertId);
        this.io.emit("alert-marked-read", { alertId });
      });

      // Receber nova análise
      socket.on("new-analysis", async (data: AnalysisRecord) => {
        await this.handleNewAnalysis(data, socket.id);
      });

      // Receber novo feedback
      socket.on("new-feedback", async (data: FeedbackRecord) => {
        await this.handleNewFeedback(data, socket.id);
      });

      // Solicitar estatísticas
      socket.on("request-statistics", async () => {
        const classStats = await getClassStatistics();
        const globalStats = await getGlobalStatistics();
        socket.emit("statistics-updated", {
          classStatistics: classStats,
          globalStatistics: globalStats,
        });
      });

      // Desconexão
      socket.on("disconnect", () => {
        console.log(`✗ Cliente desconectado: ${socket.id}`);
        this.clients.delete(socket.id);
      });
    });
  }

  private async handleNewAnalysis(analysis: AnalysisRecord, clientId: string) {
    try {
      // Salvar análise no banco de dados
      const savedAnalysis = await saveAnalysis(analysis);

      // Atualizar métricas do cliente
      const clientMetrics = this.clients.get(clientId);
      if (clientMetrics) {
        clientMetrics.analysisCount++;
        clientMetrics.lastAnalysisTime = Date.now();
        clientMetrics.avgConfidence =
          (clientMetrics.avgConfidence * (clientMetrics.analysisCount - 1) +
            analysis.confidence) /
          clientMetrics.analysisCount;
      }

      // Broadcast para todos os clientes
      this.io.emit("analysis-completed", {
        analysis: savedAnalysis,
        clientId,
        timestamp: new Date().toISOString(),
      });

      // Verificar performance
      await this.checkPerformanceAlerts(analysis.confidence);

      // Enviar notificação
      this.io.emit("notification", {
        type: "analysis",
        message: `Nova análise concluída: ${analysis.predicted_class} (${(analysis.confidence * 100).toFixed(1)}%)`,
        severity: "info",
        data: analysis,
      });
    } catch (error) {
      console.error("Erro ao processar análise:", error);
      this.io.emit("error", {
        type: "analysis_error",
        message: "Erro ao processar análise",
      });
    }
  }

  private async handleNewFeedback(feedback: FeedbackRecord, clientId: string) {
    try {
      // Salvar feedback no banco de dados
      const savedFeedback = await saveFeedback(feedback);

      // Verificar se houve erro
      const wasCorrect = feedback.predicted_class === feedback.correct_class;

      // Broadcast para todos os clientes
      this.io.emit("feedback-received", {
        feedback: savedFeedback,
        clientId,
        wasCorrect,
        timestamp: new Date().toISOString(),
      });

      // Criar alerta se houver padrão de erros
      await this.checkErrorPatterns(feedback);

      // Enviar notificação
      this.io.emit("notification", {
        type: "feedback",
        message: wasCorrect
          ? `Feedback confirmado: ${feedback.correct_class}`
          : `Correção registrada: ${feedback.predicted_class} → ${feedback.correct_class}`,
        severity: wasCorrect ? "info" : "warning",
        data: feedback,
      });
    } catch (error) {
      console.error("Erro ao processar feedback:", error);
      this.io.emit("error", {
        type: "feedback_error",
        message: "Erro ao processar feedback",
      });
    }
  }

  private async checkPerformanceAlerts(confidence: number) {
    if (confidence < this.performanceThreshold) {
      const alert: Alert = {
        type: "performance_degradation",
        message: `Performance degradada detectada: confiança ${(confidence * 100).toFixed(1)}% < ${(this.performanceThreshold * 100).toFixed(1)}%`,
        severity: "medium",
        data: { confidence, threshold: this.performanceThreshold },
        is_read: false,
      };

      await createAlert(alert);

      this.io.emit("alert", {
        ...alert,
        timestamp: new Date().toISOString(),
      });
    }
  }

  private async checkErrorPatterns(feedback: FeedbackRecord) {
    // Verificar se há padrão de erros para a mesma classe
    const classStats = await getClassStatistics();
    const classStat = classStats.find((s) => s.class === feedback.correct_class);

    if (classStat && classStat.total > 10) {
      const errorRate = classStat.incorrect / classStat.total;

      if (errorRate > 0.2) {
        // Mais de 20% de erro
        const alert: Alert = {
          type: "retrain_recommended",
          message: `Taxa de erro alta para ${feedback.correct_class}: ${(errorRate * 100).toFixed(1)}%. Retreinamento recomendado.`,
          severity: "high",
          data: {
            class: feedback.correct_class,
            errorRate,
            totalSamples: classStat.total,
          },
          is_read: false,
        };

        await createAlert(alert);

        this.io.emit("alert", {
          ...alert,
          timestamp: new Date().toISOString(),
        });
      }
    }
  }

  public async broadcastStatisticsUpdate() {
    const classStats = await getClassStatistics();
    const globalStats = await getGlobalStatistics();

    this.io.emit("statistics-updated", {
      classStatistics: classStats,
      globalStatistics: globalStats,
      timestamp: new Date().toISOString(),
    });
  }

  public async broadcastAlert(alert: Alert) {
    this.io.emit("alert", {
      ...alert,
      timestamp: new Date().toISOString(),
    });
  }

  public getConnectedClientsCount(): number {
    return this.clients.size;
  }

  public getClientMetrics(clientId: string): ClientMetrics | undefined {
    return this.clients.get(clientId);
  }

  public getAllClientMetrics(): ClientMetrics[] {
    return Array.from(this.clients.values());
  }
}

export default WebSocketManager;
