import { eq, desc, and } from "drizzle-orm";
import { getDb } from "./db";
import {
  analyses,
  feedbacks,
  classStatistics,
  alerts,
  modelVersions,
  InsertAnalysis,
  InsertFeedback,
  InsertAlert,
  InsertModelVersion,
} from "../drizzle/schema";

/**
 * Salvar análise QML no banco de dados
 */
export async function saveAnalysisToDb(data: InsertAnalysis) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const result = await db.insert(analyses).values(data);
  return result;
}

/**
 * Obter histórico de análises
 */
export async function getAnalysisHistory(userId: number, limit: number = 100) {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(analyses)
    .where(eq(analyses.userId, userId))
    .orderBy(desc(analyses.createdAt))
    .limit(limit);
}

/**
 * Salvar feedback de correção
 */
export async function saveFeedbackToDb(data: InsertFeedback) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const result = await db.insert(feedbacks).values(data);

  // Atualizar estatísticas da classe
  await updateClassStatistics(data.correctClass, data.predictedClass === data.correctClass);

  return result;
}

/**
 * Obter histórico de feedback
 */
export async function getFeedbackHistory(userId: number, limit: number = 100) {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(feedbacks)
    .where(eq(feedbacks.userId, userId))
    .orderBy(desc(feedbacks.createdAt))
    .limit(limit);
}

/**
 * Atualizar estatísticas de uma classe
 */
export async function updateClassStatistics(className: string, isCorrect: boolean) {
  const db = await getDb();
  if (!db) return;

  // Obter estatísticas atuais
  const current = await db
    .select()
    .from(classStatistics)
    .where(eq(classStatistics.className, className))
    .limit(1);

  if (current.length === 0) {
    // Criar nova entrada
    await db.insert(classStatistics).values({
      className,
      total: 1,
      correct: isCorrect ? 1 : 0,
      incorrect: isCorrect ? 0 : 1,
      accuracy: isCorrect ? 1.0 : 0.0,
    });
  } else {
    // Atualizar entrada existente
    const stat = current[0];
    const newTotal = stat.total + 1;
    const newCorrect = stat.correct + (isCorrect ? 1 : 0);
    const newIncorrect = stat.incorrect + (isCorrect ? 0 : 1);
    const newAccuracy = newCorrect / newTotal;

    // Calcular precisão e recall (simplificado)
    const newPrecision = newCorrect / newTotal;
    const newRecall = newCorrect / newTotal;
    const newF1 = 2 * (newPrecision * newRecall) / (newPrecision + newRecall || 1);

    await db
      .update(classStatistics)
      .set({
        total: newTotal,
        correct: newCorrect,
        incorrect: newIncorrect,
        accuracy: newAccuracy,
        precision: newPrecision,
        recall: newRecall,
        f1Score: newF1,
      })
      .where(eq(classStatistics.className, className));
  }
}

/**
 * Obter estatísticas de todas as classes
 */
export async function getClassStatisticsFromDb() {
  const db = await getDb();
  if (!db) return [];

  return await db.select().from(classStatistics).orderBy(classStatistics.className);
}

/**
 * Obter estatísticas globais
 */
export async function getGlobalStatisticsFromDb() {
  const db = await getDb();
  if (!db) return {};

  const analysesData = await db.select().from(analyses);
  const feedbacksData = await db.select().from(feedbacks);
  const classStatsData = await db.select().from(classStatistics);

  const totalAnalyses = analysesData.length;
  const totalFeedback = feedbacksData.length;
  const correctFeedback = feedbacksData.filter(
    (f) => f.predictedClass === f.correctClass
  ).length;
  const incorrectFeedback = totalFeedback - correctFeedback;

  const avgConfidence =
    analysesData.length > 0
      ? analysesData.reduce((sum, a) => sum + a.confidence, 0) / analysesData.length
      : 0;

  const globalAccuracy =
    totalFeedback > 0 ? (correctFeedback / totalFeedback) * 100 : 0;

  return {
    totalAnalyses,
    totalFeedback,
    correctFeedback,
    incorrectFeedback,
    avgConfidence,
    globalAccuracy,
    classStatistics: classStatsData,
  };
}

/**
 * Criar alerta
 */
export async function createAlertInDb(data: InsertAlert) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  return await db.insert(alerts).values(data);
}

/**
 * Obter alertas não lidos
 */
export async function getUnreadAlerts(userId?: number) {
  const db = await getDb();
  if (!db) return [];

  if (userId) {
    return await db
      .select()
      .from(alerts)
      .where(and(eq(alerts.isRead, false), eq(alerts.userId, userId)))
      .orderBy(desc(alerts.createdAt));
  }

  return await db
    .select()
    .from(alerts)
    .where(eq(alerts.isRead, false))
    .orderBy(desc(alerts.createdAt));
}

/**
 * Marcar alerta como lido
 */
export async function markAlertAsRead(alertId: number) {
  const db = await getDb();
  if (!db) return;

  await db.update(alerts).set({ isRead: true }).where(eq(alerts.id, alertId));
}

/**
 * Salvar versão do modelo
 */
export async function saveModelVersionToDb(data: InsertModelVersion) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  return await db.insert(modelVersions).values(data);
}

/**
 * Obter versões do modelo
 */
export async function getModelVersionsFromDb() {
  const db = await getDb();
  if (!db) return [];

  return await db.select().from(modelVersions).orderBy(desc(modelVersions.createdAt));
}

/**
 * Ativar versão do modelo
 */
export async function activateModelVersion(version: string) {
  const db = await getDb();
  if (!db) return;

  // Desativar todas as versões
  await db.update(modelVersions).set({ isActive: false });

  // Ativar a versão especificada
  await db
    .update(modelVersions)
    .set({ isActive: true })
    .where(eq(modelVersions.version, version));
}

export default {
  saveAnalysisToDb,
  getAnalysisHistory,
  saveFeedbackToDb,
  getFeedbackHistory,
  updateClassStatistics,
  getClassStatisticsFromDb,
  getGlobalStatisticsFromDb,
  createAlertInDb,
  getUnreadAlerts,
  markAlertAsRead,
  saveModelVersionToDb,
  getModelVersionsFromDb,
  activateModelVersion,
};
