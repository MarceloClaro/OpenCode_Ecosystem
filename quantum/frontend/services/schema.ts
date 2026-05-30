import { int, mysqlEnum, mysqlTable, text, timestamp, varchar, float, boolean, json } from "drizzle-orm/mysql-core";
import { relations } from "drizzle-orm";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

// Análises QML
export const analyses = mysqlTable("analyses", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  imageName: varchar("imageName", { length: 255 }).notNull(),
  predictedClass: varchar("predictedClass", { length: 50 }).notNull(),
  confidence: float("confidence").notNull(),
  inferenceTime: float("inferenceTime").notNull(),
  modelVersion: varchar("modelVersion", { length: 20 }).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type Analysis = typeof analyses.$inferSelect;
export type InsertAnalysis = typeof analyses.$inferInsert;

// Feedback de Correções
export const feedbacks = mysqlTable("feedbacks", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  analysisId: int("analysisId"),
  imageName: varchar("imageName", { length: 255 }).notNull(),
  predictedClass: varchar("predictedClass", { length: 50 }).notNull(),
  correctClass: varchar("correctClass", { length: 50 }).notNull(),
  confidence: float("confidence").notNull(),
  notes: text("notes"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type Feedback = typeof feedbacks.$inferSelect;
export type InsertFeedback = typeof feedbacks.$inferInsert;

// Estatísticas por Classe
export const classStatistics = mysqlTable("classStatistics", {
  id: int("id").autoincrement().primaryKey(),
  className: varchar("className", { length: 50 }).notNull().unique(),
  total: int("total").default(0).notNull(),
  correct: int("correct").default(0).notNull(),
  incorrect: int("incorrect").default(0).notNull(),
  accuracy: float("accuracy").default(0).notNull(),
  precision: float("precision").default(0).notNull(),
  recall: float("recall").default(0).notNull(),
  f1Score: float("f1Score").default(0).notNull(),
  lastUpdated: timestamp("lastUpdated").defaultNow().onUpdateNow().notNull(),
});

export type ClassStatistic = typeof classStatistics.$inferSelect;
export type InsertClassStatistic = typeof classStatistics.$inferInsert;

// Alertas do Sistema
export const alerts = mysqlTable("alerts", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId"),
  type: mysqlEnum("type", ["performance_degradation", "retrain_recommended", "error"]).notNull(),
  message: text("message").notNull(),
  severity: mysqlEnum("severity", ["low", "medium", "high"]).notNull(),
  data: json("data"),
  isRead: boolean("isRead").default(false).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type Alert = typeof alerts.$inferSelect;
export type InsertAlert = typeof alerts.$inferInsert;

// Versões do Modelo
export const modelVersions = mysqlTable("modelVersions", {
  id: int("id").autoincrement().primaryKey(),
  version: varchar("version", { length: 20 }).notNull().unique(),
  accuracy: float("accuracy").notNull(),
  f1Score: float("f1Score").notNull(),
  aucRoc: float("aucRoc").notNull(),
  cvAccuracy: varchar("cvAccuracy", { length: 50 }),
  bootstrapCi: varchar("bootstrapCi", { length: 50 }),
  isActive: boolean("isActive").default(false).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type ModelVersion = typeof modelVersions.$inferSelect;
export type InsertModelVersion = typeof modelVersions.$inferInsert;

// Relações
export const usersRelations = relations(users, ({ many }) => ({
  analyses: many(analyses),
  feedbacks: many(feedbacks),
  alerts: many(alerts),
}));

export const analysesRelations = relations(analyses, ({ one, many }) => ({
  user: one(users, {
    fields: [analyses.userId],
    references: [users.id],
  }),
  feedback: many(feedbacks),
}));

export const feedbacksRelations = relations(feedbacks, ({ one }) => ({
  user: one(users, {
    fields: [feedbacks.userId],
    references: [users.id],
  }),
  analysis: one(analyses, {
    fields: [feedbacks.analysisId],
    references: [analyses.id],
  }),
}));

export const alertsRelations = relations(alerts, ({ one }) => ({
  user: one(users, {
    fields: [alerts.userId],
    references: [users.id],
  }),
}));

// TODO: Add your tables here