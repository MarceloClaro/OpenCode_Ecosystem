import { z } from "zod";
import { protectedProcedure, publicProcedure, router } from "./_core/trpc";
import {
  saveAnalysisToDb,
  getAnalysisHistory,
  saveFeedbackToDb,
  getFeedbackHistory,
  getClassStatisticsFromDb,
  getGlobalStatisticsFromDb,
  createAlertInDb,
  getUnreadAlerts,
  markAlertAsRead,
  saveModelVersionToDb,
  getModelVersionsFromDb,
  activateModelVersion,
} from "./qml-db";

export const qmlRouter = router({
  // Salvar análise
  saveAnalysis: protectedProcedure
    .input(
      z.object({
        imageName: z.string(),
        predictedClass: z.string(),
        confidence: z.number(),
        inferenceTime: z.number(),
        modelVersion: z.string(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      try {
        await saveAnalysisToDb({
          userId: ctx.user.id,
          imageName: input.imageName,
          predictedClass: input.predictedClass,
          confidence: input.confidence,
          inferenceTime: input.inferenceTime,
          modelVersion: input.modelVersion,
        });

        return { status: "success", message: "Análise salva com sucesso" };
      } catch (error) {
        console.error("Error saving analysis:", error);
        return { status: "error", message: "Erro ao salvar análise" };
      }
    }),

  // Obter histórico de análises
  getAnalysisHistory: protectedProcedure
    .input(z.object({ limit: z.number().default(100) }))
    .query(async ({ ctx, input }) => {
      try {
        const history = await getAnalysisHistory(ctx.user.id, input.limit);
        return { status: "success", data: history };
      } catch (error) {
        console.error("Error getting analysis history:", error);
        return { status: "error", data: [] };
      }
    }),

  // Salvar feedback
  saveFeedback: protectedProcedure
    .input(
      z.object({
        imageName: z.string(),
        predictedClass: z.string(),
        correctClass: z.string(),
        confidence: z.number(),
        notes: z.string().optional(),
        analysisId: z.number().optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      try {
        await saveFeedbackToDb({
          userId: ctx.user.id,
          imageName: input.imageName,
          predictedClass: input.predictedClass,
          correctClass: input.correctClass,
          confidence: input.confidence,
          notes: input.notes,
          analysisId: input.analysisId,
        });

        return { status: "success", message: "Feedback salvo com sucesso" };
      } catch (error) {
        console.error("Error saving feedback:", error);
        return { status: "error", message: "Erro ao salvar feedback" };
      }
    }),

  // Obter histórico de feedback
  getFeedbackHistory: protectedProcedure
    .input(z.object({ limit: z.number().default(100) }))
    .query(async ({ ctx, input }) => {
      try {
        const history = await getFeedbackHistory(ctx.user.id, input.limit);
        return { status: "success", data: history };
      } catch (error) {
        console.error("Error getting feedback history:", error);
        return { status: "error", data: [] };
      }
    }),

  // Obter estatísticas de classes
  getClassStatistics: publicProcedure.query(async () => {
    try {
      const stats = await getClassStatisticsFromDb();
      return { status: "success", data: stats };
    } catch (error) {
      console.error("Error getting class statistics:", error);
      return { status: "error", data: [] };
    }
  }),

  // Obter estatísticas globais
  getGlobalStatistics: publicProcedure.query(async () => {
    try {
      const stats = await getGlobalStatisticsFromDb();
      return { status: "success", data: stats };
    } catch (error) {
      console.error("Error getting global statistics:", error);
      return { status: "error", data: {} };
    }
  }),

  // Criar alerta
  createAlert: protectedProcedure
    .input(
      z.object({
        type: z.enum(["performance_degradation", "retrain_recommended", "error"]),
        message: z.string(),
        severity: z.enum(["low", "medium", "high"]),
        data: z.any().optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      try {
        await createAlertInDb({
          userId: ctx.user.id,
          type: input.type,
          message: input.message,
          severity: input.severity,
          data: input.data,
        });

        return { status: "success", message: "Alerta criado com sucesso" };
      } catch (error) {
        console.error("Error creating alert:", error);
        return { status: "error", message: "Erro ao criar alerta" };
      }
    }),

  // Obter alertas não lidos
  getUnreadAlerts: protectedProcedure.query(async ({ ctx }) => {
    try {
      const alerts = await getUnreadAlerts(ctx.user.id);
      return { status: "success", data: alerts };
    } catch (error) {
      console.error("Error getting unread alerts:", error);
      return { status: "error", data: [] };
    }
  }),

  // Marcar alerta como lido
  markAlertAsRead: protectedProcedure
    .input(z.object({ alertId: z.number() }))
    .mutation(async ({ ctx, input }) => {
      try {
        await markAlertAsRead(input.alertId);
        return { status: "success", message: "Alerta marcado como lido" };
      } catch (error) {
        console.error("Error marking alert as read:", error);
        return { status: "error", message: "Erro ao marcar alerta" };
      }
    }),

  // Salvar versão do modelo
  saveModelVersion: protectedProcedure
    .input(
      z.object({
        version: z.string(),
        accuracy: z.number(),
        f1Score: z.number(),
        aucRoc: z.number(),
        cvAccuracy: z.string().optional(),
        bootstrapCi: z.string().optional(),
      })
    )
    .mutation(async ({ input }) => {
      try {
        await saveModelVersionToDb({
          version: input.version,
          accuracy: input.accuracy,
          f1Score: input.f1Score,
          aucRoc: input.aucRoc,
          cvAccuracy: input.cvAccuracy,
          bootstrapCi: input.bootstrapCi,
        });

        return { status: "success", message: "Versão do modelo salva com sucesso" };
      } catch (error) {
        console.error("Error saving model version:", error);
        return { status: "error", message: "Erro ao salvar versão do modelo" };
      }
    }),

  // Obter versões do modelo
  getModelVersions: publicProcedure.query(async () => {
    try {
      const versions = await getModelVersionsFromDb();
      return { status: "success", data: versions };
    } catch (error) {
      console.error("Error getting model versions:", error);
      return { status: "error", data: [] };
    }
  }),

  // Ativar versão do modelo
  activateModelVersion: protectedProcedure
    .input(z.object({ version: z.string() }))
    .mutation(async ({ input }) => {
      try {
        await activateModelVersion(input.version);
        return { status: "success", message: "Versão do modelo ativada com sucesso" };
      } catch (error) {
        console.error("Error activating model version:", error);
        return { status: "error", message: "Erro ao ativar versão do modelo" };
      }
    }),
});

export default qmlRouter;
