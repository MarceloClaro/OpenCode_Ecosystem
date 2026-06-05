import { Pool, QueryResult } from "pg";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuração do banco de dados
const pool = new Pool({
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "postgres",
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5432"),
  database: process.env.DB_NAME || "qml_medical",
});

// Tipos
export interface FeedbackRecord {
  id?: string;
  image_name: string;
  predicted_class: string;
  correct_class: string;
  confidence: number;
  notes: string;
  timestamp?: string;
}

export interface AnalysisRecord {
  id?: string;
  image_name: string;
  predicted_class: string;
  confidence: number;
  inference_time: number;
  model_version: string;
  timestamp?: string;
}

export interface ClassStatistic {
  class: string;
  total: number;
  correct: number;
  incorrect: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  last_updated?: string;
}

export interface Alert {
  id?: string;
  type: "performance_degradation" | "retrain_recommended" | "error";
  message: string;
  severity: "low" | "medium" | "high";
  data?: Record<string, any>;
  is_read: boolean;
  timestamp?: string;
}

// Inicializar banco de dados
export async function initializeDatabase() {
  try {
    // Criar tabelas
    await pool.query(`
      CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        image_name VARCHAR(255) NOT NULL,
        predicted_class VARCHAR(50) NOT NULL,
        correct_class VARCHAR(50) NOT NULL,
        confidence FLOAT NOT NULL,
        notes TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS analyses (
        id SERIAL PRIMARY KEY,
        image_name VARCHAR(255) NOT NULL,
        predicted_class VARCHAR(50) NOT NULL,
        confidence FLOAT NOT NULL,
        inference_time FLOAT NOT NULL,
        model_version VARCHAR(20) NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS class_statistics (
        id SERIAL PRIMARY KEY,
        class VARCHAR(50) NOT NULL UNIQUE,
        total INTEGER DEFAULT 0,
        correct INTEGER DEFAULT 0,
        incorrect INTEGER DEFAULT 0,
        accuracy FLOAT DEFAULT 0,
        precision FLOAT DEFAULT 0,
        recall FLOAT DEFAULT 0,
        f1 FLOAT DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS alerts (
        id SERIAL PRIMARY KEY,
        type VARCHAR(50) NOT NULL,
        message TEXT NOT NULL,
        severity VARCHAR(20) NOT NULL,
        data JSONB,
        is_read BOOLEAN DEFAULT FALSE,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS model_versions (
        id SERIAL PRIMARY KEY,
        version VARCHAR(20) NOT NULL UNIQUE,
        accuracy FLOAT NOT NULL,
        f1_score FLOAT NOT NULL,
        auc_roc FLOAT NOT NULL,
        cv_accuracy VARCHAR(50),
        bootstrap_ci VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT FALSE
      );

      -- Criar índices
      CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp);
      CREATE INDEX IF NOT EXISTS idx_analyses_timestamp ON analyses(timestamp);
      CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
      CREATE INDEX IF NOT EXISTS idx_alerts_is_read ON alerts(is_read);
    `);

    // Inserir classes padrão
    const classes = ["MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC"];
    for (const cls of classes) {
      await pool.query(
        `INSERT INTO class_statistics (class) VALUES ($1) ON CONFLICT DO NOTHING`,
        [cls]
      );
    }

    console.log("✓ Banco de dados inicializado com sucesso");
    return true;
  } catch (error) {
    console.error("Erro ao inicializar banco de dados:", error);
    return false;
  }
}

// Operações de Feedback
export async function saveFeedback(feedback: FeedbackRecord): Promise<FeedbackRecord | null> {
  try {
    const result = await pool.query(
      `INSERT INTO feedback (image_name, predicted_class, correct_class, confidence, notes)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING id, image_name, predicted_class, correct_class, confidence, notes, timestamp`,
      [
        feedback.image_name,
        feedback.predicted_class,
        feedback.correct_class,
        feedback.confidence,
        feedback.notes,
      ]
    );

    // Atualizar estatísticas
    await updateClassStatistics(feedback.correct_class, feedback.predicted_class === feedback.correct_class);

    return result.rows[0];
  } catch (error) {
    console.error("Erro ao salvar feedback:", error);
    return null;
  }
}

export async function getFeedbackHistory(limit: number = 100): Promise<FeedbackRecord[]> {
  try {
    const result = await pool.query(
      `SELECT id, image_name, predicted_class, correct_class, confidence, notes, timestamp
       FROM feedback
       ORDER BY timestamp DESC
       LIMIT $1`,
      [limit]
    );
    return result.rows;
  } catch (error) {
    console.error("Erro ao obter histórico de feedback:", error);
    return [];
  }
}

// Operações de Análises
export async function saveAnalysis(analysis: AnalysisRecord): Promise<AnalysisRecord | null> {
  try {
    const result = await pool.query(
      `INSERT INTO analyses (image_name, predicted_class, confidence, inference_time, model_version)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING id, image_name, predicted_class, confidence, inference_time, model_version, timestamp`,
      [
        analysis.image_name,
        analysis.predicted_class,
        analysis.confidence,
        analysis.inference_time,
        analysis.model_version,
      ]
    );
    return result.rows[0];
  } catch (error) {
    console.error("Erro ao salvar análise:", error);
    return null;
  }
}

export async function getAnalysisHistory(limit: number = 100): Promise<AnalysisRecord[]> {
  try {
    const result = await pool.query(
      `SELECT id, image_name, predicted_class, confidence, inference_time, model_version, timestamp
       FROM analyses
       ORDER BY timestamp DESC
       LIMIT $1`,
      [limit]
    );
    return result.rows;
  } catch (error) {
    console.error("Erro ao obter histórico de análises:", error);
    return [];
  }
}

// Operações de Estatísticas
export async function updateClassStatistics(
  className: string,
  isCorrect: boolean
): Promise<void> {
  try {
    await pool.query(
      `UPDATE class_statistics
       SET total = total + 1,
           correct = correct + $1,
           incorrect = incorrect + $2,
           accuracy = CAST(correct + $1 AS FLOAT) / (total + 1),
           last_updated = CURRENT_TIMESTAMP
       WHERE class = $3`,
      [isCorrect ? 1 : 0, isCorrect ? 0 : 1, className]
    );
  } catch (error) {
    console.error("Erro ao atualizar estatísticas:", error);
  }
}

export async function getClassStatistics(): Promise<ClassStatistic[]> {
  try {
    const result = await pool.query(
      `SELECT class, total, correct, incorrect, accuracy, precision, recall, f1, last_updated
       FROM class_statistics
       ORDER BY class ASC`
    );
    return result.rows;
  } catch (error) {
    console.error("Erro ao obter estatísticas:", error);
    return [];
  }
}

export async function getGlobalStatistics(): Promise<Record<string, any>> {
  try {
    const result = await pool.query(`
      SELECT
        COUNT(*) as total_analyses,
        COUNT(DISTINCT image_name) as unique_images,
        AVG(confidence) as avg_confidence,
        MAX(confidence) as max_confidence,
        MIN(confidence) as min_confidence
      FROM analyses
    `);

    const feedbackResult = await pool.query(`
      SELECT
        COUNT(*) as total_feedback,
        SUM(CASE WHEN predicted_class = correct_class THEN 1 ELSE 0 END) as correct_feedback,
        SUM(CASE WHEN predicted_class != correct_class THEN 1 ELSE 0 END) as incorrect_feedback
      FROM feedback
    `);

    return {
      ...result.rows[0],
      ...feedbackResult.rows[0],
    };
  } catch (error) {
    console.error("Erro ao obter estatísticas globais:", error);
    return {};
  }
}

// Operações de Alertas
export async function createAlert(alert: Alert): Promise<Alert | null> {
  try {
    const result = await pool.query(
      `INSERT INTO alerts (type, message, severity, data, is_read)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING id, type, message, severity, data, is_read, timestamp`,
      [alert.type, alert.message, alert.severity, JSON.stringify(alert.data || {}), false]
    );
    return result.rows[0];
  } catch (error) {
    console.error("Erro ao criar alerta:", error);
    return null;
  }
}

export async function getAlerts(unreadOnly: boolean = false): Promise<Alert[]> {
  try {
    let query = `SELECT id, type, message, severity, data, is_read, timestamp FROM alerts`;
    if (unreadOnly) {
      query += ` WHERE is_read = FALSE`;
    }
    query += ` ORDER BY timestamp DESC LIMIT 100`;

    const result = await pool.query(query);
    return result.rows;
  } catch (error) {
    console.error("Erro ao obter alertas:", error);
    return [];
  }
}

export async function markAlertAsRead(alertId: number): Promise<void> {
  try {
    await pool.query(`UPDATE alerts SET is_read = TRUE WHERE id = $1`, [alertId]);
  } catch (error) {
    console.error("Erro ao marcar alerta como lido:", error);
  }
}

// Operações de Versões do Modelo
export async function saveModelVersion(version: string, metrics: Record<string, any>): Promise<void> {
  try {
    await pool.query(
      `INSERT INTO model_versions (version, accuracy, f1_score, auc_roc, cv_accuracy, bootstrap_ci)
       VALUES ($1, $2, $3, $4, $5, $6)
       ON CONFLICT (version) DO UPDATE SET
         accuracy = $2,
         f1_score = $3,
         auc_roc = $4,
         cv_accuracy = $5,
         bootstrap_ci = $6`,
      [
        version,
        metrics.accuracy || 0,
        metrics.f1_score || 0,
        metrics.auc_roc || 0,
        metrics.cv_accuracy || "",
        metrics.bootstrap_ci || "",
      ]
    );
  } catch (error) {
    console.error("Erro ao salvar versão do modelo:", error);
  }
}

export async function getModelVersions(): Promise<Record<string, any>[]> {
  try {
    const result = await pool.query(
      `SELECT version, accuracy, f1_score, auc_roc, cv_accuracy, bootstrap_ci, created_at, is_active
       FROM model_versions
       ORDER BY created_at DESC`
    );
    return result.rows;
  } catch (error) {
    console.error("Erro ao obter versões do modelo:", error);
    return [];
  }
}

// Fechar conexão
export async function closeDatabase(): Promise<void> {
  try {
    await pool.end();
    console.log("Conexão com banco de dados fechada");
  } catch (error) {
    console.error("Erro ao fechar banco de dados:", error);
  }
}

export default pool;
