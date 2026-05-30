import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { AlertCircle, Download, TrendingUp, Users, CheckCircle2, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";

interface FeedbackRecord {
  id: string;
  timestamp: string;
  imageName: string;
  predictedClass: string;
  correctClass: string;
  confidence: number;
  notes: string;
}

interface ClassStatistics {
  class: string;
  total: number;
  correct: number;
  incorrect: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
}

export default function AdminDashboard() {
  const [feedbackHistory, setFeedbackHistory] = useState<FeedbackRecord[]>([]);
  const [classStats, setClassStats] = useState<ClassStatistics[]>([]);
  const [selectedTab, setSelectedTab] = useState("overview");
  const [isExporting, setIsExporting] = useState(false);

  // Simular carregamento de dados
  useEffect(() => {
    // Dados de exemplo
    const mockFeedback: FeedbackRecord[] = [
      {
        id: "1",
        timestamp: new Date().toISOString(),
        imageName: "lesion_001.jpg",
        predictedClass: "MEL",
        correctClass: "NV",
        confidence: 85.2,
        notes: "Classificação incorreta - era nevo, não melanoma"
      },
      {
        id: "2",
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        imageName: "lesion_002.jpg",
        predictedClass: "BCC",
        correctClass: "BCC",
        confidence: 92.1,
        notes: "Classificação correta"
      },
      {
        id: "3",
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        imageName: "lesion_003.jpg",
        predictedClass: "AKIEC",
        correctClass: "BKL",
        confidence: 78.5,
        notes: "Erro de classificação - ceratose benigna"
      },
    ];

    const mockStats: ClassStatistics[] = [
      { class: "MEL", total: 145, correct: 134, incorrect: 11, accuracy: 92.4, precision: 0.931, recall: 0.924, f1: 0.927 },
      { class: "NV", total: 168, correct: 159, incorrect: 9, accuracy: 94.6, precision: 0.949, recall: 0.946, f1: 0.948 },
      { class: "BCC", total: 112, correct: 98, incorrect: 14, accuracy: 87.5, precision: 0.878, recall: 0.875, f1: 0.876 },
      { class: "AKIEC", total: 89, correct: 75, incorrect: 14, accuracy: 84.3, precision: 0.847, recall: 0.843, f1: 0.845 },
      { class: "BKL", total: 134, correct: 121, incorrect: 13, accuracy: 90.3, precision: 0.905, recall: 0.903, f1: 0.904 },
      { class: "DF", total: 95, correct: 82, incorrect: 13, accuracy: 86.3, precision: 0.865, recall: 0.863, f1: 0.864 },
      { class: "VASC", total: 78, correct: 72, incorrect: 6, accuracy: 92.3, precision: 0.923, recall: 0.923, f1: 0.923 },
    ];

    setFeedbackHistory(mockFeedback);
    setClassStats(mockStats);
  }, []);

  // Calcular métricas globais
  const totalFeedback = feedbackHistory.length;
  const correctFeedback = feedbackHistory.filter(f => f.predictedClass === f.correctClass).length;
  const globalAccuracy = totalFeedback > 0 ? (correctFeedback / totalFeedback * 100).toFixed(2) : "0.00";

  // Dados para gráfico de acurácia por classe
  const accuracyByClass = classStats.map(stat => ({
    class: stat.class,
    accuracy: (stat.accuracy * 100).toFixed(1),
    precision: (stat.precision * 100).toFixed(1),
    recall: (stat.recall * 100).toFixed(1),
  }));

  // Dados para gráfico de distribuição de erros
  const errorDistribution = classStats.map(stat => ({
    class: stat.class,
    erros: stat.incorrect,
    acertos: stat.correct,
  }));

  // Dados para gráfico de tendência temporal
  const trendData = [
    { período: "Semana 1", acurácia: 87.5, f1: 0.872 },
    { período: "Semana 2", acurácia: 88.2, f1: 0.881 },
    { período: "Semana 3", acurácia: 89.1, f1: 0.889 },
    { período: "Semana 4", acurácia: 90.3, f1: 0.903 },
    { período: "Semana 5", acurácia: 91.2, f1: 0.912 },
  ];

  const handleExportReport = async () => {
    setIsExporting(true);
    try {
      // Simular geração de relatório
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const report = {
        timestamp: new Date().toISOString(),
        globalAccuracy: globalAccuracy,
        totalFeedback,
        classStatistics: classStats,
        feedbackHistory,
      };

      // Criar arquivo JSON
      const element = document.createElement("a");
      element.setAttribute("href", "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2)));
      element.setAttribute("download", `qml_report_${Date.now()}.json`);
      element.style.display = "none";
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);

      toast.success("Relatório exportado com sucesso!");
    } catch (error) {
      toast.error("Erro ao exportar relatório");
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportPDF = async () => {
    setIsExporting(true);
    try {
      // Simular geração de PDF
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success("PDF gerado com sucesso!");
    } catch (error) {
      toast.error("Erro ao gerar PDF");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-2"
        >
          <h1 className="text-4xl font-bold text-cyan-400">Dashboard de Administração</h1>
          <p className="text-gray-400">Monitoramento de performance e histórico de feedback do modelo QML</p>
        </motion.div>

        {/* Métricas Globais */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4"
        >
          <Card className="bg-slate-800/50 border-cyan-500/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-400 mb-1">Acurácia Global</p>
                  <p className="text-3xl font-bold text-cyan-400">{globalAccuracy}%</p>
                </div>
                <CheckCircle2 className="w-10 h-10 text-green-400 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-cyan-500/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-400 mb-1">Total de Feedback</p>
                  <p className="text-3xl font-bold text-cyan-400">{totalFeedback}</p>
                </div>
                <Users className="w-10 h-10 text-purple-400 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-cyan-500/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-400 mb-1">Classificações Corretas</p>
                  <p className="text-3xl font-bold text-green-400">{correctFeedback}</p>
                </div>
                <TrendingUp className="w-10 h-10 text-green-400 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-red-500/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-400 mb-1">Classificações Erradas</p>
                  <p className="text-3xl font-bold text-red-400">{totalFeedback - correctFeedback}</p>
                </div>
                <AlertTriangle className="w-10 h-10 text-red-400 opacity-50" />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Abas de Análise */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-4">
            <TabsList className="bg-slate-800/50 border border-cyan-500/20">
              <TabsTrigger value="overview" className="data-[state=active]:bg-cyan-500/20">
                Visão Geral
              </TabsTrigger>
              <TabsTrigger value="classes" className="data-[state=active]:bg-cyan-500/20">
                Por Classe
              </TabsTrigger>
              <TabsTrigger value="trends" className="data-[state=active]:bg-cyan-500/20">
                Tendências
              </TabsTrigger>
              <TabsTrigger value="feedback" className="data-[state=active]:bg-cyan-500/20">
                Histórico
              </TabsTrigger>
            </TabsList>

            {/* Visão Geral */}
            <TabsContent value="overview" className="space-y-4">
              <Card className="bg-slate-800/50 border-cyan-500/20">
                <CardHeader>
                  <CardTitle className="text-cyan-400">Distribuição de Acertos e Erros por Classe</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={errorDistribution}>
                      <CartesianGrid stroke="#334155" />
                      <XAxis dataKey="class" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #00d9ff" }} />
                      <Legend />
                      <Bar dataKey="acertos" fill="#10b981" name="Acertos" />
                      <Bar dataKey="erros" fill="#ef4444" name="Erros" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Por Classe */}
            <TabsContent value="classes" className="space-y-4">
              <Card className="bg-slate-800/50 border-cyan-500/20">
                <CardHeader>
                  <CardTitle className="text-cyan-400">Métricas por Classe Diagnóstica</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={accuracyByClass}>
                      <CartesianGrid stroke="#334155" />
                      <XAxis dataKey="class" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" domain={[0, 100]} />
                      <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #00d9ff" }} />
                      <Legend />
                      <Bar dataKey="accuracy" fill="#00d9ff" name="Acurácia (%)" />
                      <Bar dataKey="precision" fill="#9d4edd" name="Precisão (%)" />
                      <Bar dataKey="recall" fill="#10b981" name="Recall (%)" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Tabela Detalhada */}
              <Card className="bg-slate-800/50 border-cyan-500/20">
                <CardHeader>
                  <CardTitle className="text-cyan-400">Estatísticas Detalhadas</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-cyan-500/20">
                          <th className="text-left py-2 text-cyan-400">Classe</th>
                          <th className="text-center py-2 text-cyan-400">Total</th>
                          <th className="text-center py-2 text-cyan-400">Acertos</th>
                          <th className="text-center py-2 text-cyan-400">Erros</th>
                          <th className="text-center py-2 text-cyan-400">Acurácia</th>
                          <th className="text-center py-2 text-cyan-400">Precisão</th>
                          <th className="text-center py-2 text-cyan-400">Recall</th>
                          <th className="text-center py-2 text-cyan-400">F1-Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {classStats.map((stat) => (
                          <tr key={stat.class} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                            <td className="py-3 text-cyan-300 font-semibold">{stat.class}</td>
                            <td className="text-center text-gray-400">{stat.total}</td>
                            <td className="text-center text-green-400">{stat.correct}</td>
                            <td className="text-center text-red-400">{stat.incorrect}</td>
                            <td className="text-center text-cyan-400">{(stat.accuracy * 100).toFixed(1)}%</td>
                            <td className="text-center text-cyan-400">{(stat.precision * 100).toFixed(1)}%</td>
                            <td className="text-center text-cyan-400">{(stat.recall * 100).toFixed(1)}%</td>
                            <td className="text-center text-cyan-400">{(stat.f1 * 100).toFixed(1)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Tendências */}
            <TabsContent value="trends" className="space-y-4">
              <Card className="bg-slate-800/50 border-cyan-500/20">
                <CardHeader>
                  <CardTitle className="text-cyan-400">Evolução de Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={trendData}>
                      <CartesianGrid stroke="#334155" />
                      <XAxis dataKey="período" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" domain={[85, 92]} />
                      <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #00d9ff" }} />
                      <Legend />
                      <Line type="monotone" dataKey="acurácia" stroke="#00d9ff" name="Acurácia (%)" strokeWidth={2} />
                      <Line type="monotone" dataKey="f1" stroke="#9d4edd" name="F1-Score" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Histórico de Feedback */}
            <TabsContent value="feedback" className="space-y-4">
              <Card className="bg-slate-800/50 border-cyan-500/20">
                <CardHeader>
                  <CardTitle className="text-cyan-400">Histórico de Correções</CardTitle>
                  <CardDescription>Últimas correções de classificação enviadas</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {feedbackHistory.map((feedback) => (
                      <div
                        key={feedback.id}
                        className="p-4 bg-slate-700/30 border border-slate-600/50 rounded-lg hover:border-cyan-500/30 transition-all"
                      >
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                          <div>
                            <p className="text-xs text-gray-400">Arquivo</p>
                            <p className="text-sm font-semibold text-cyan-300">{feedback.imageName}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-400">Predito</p>
                            <p className="text-sm font-semibold text-red-400">{feedback.predictedClass}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-400">Correto</p>
                            <p className="text-sm font-semibold text-green-400">{feedback.correctClass}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-400">Confiança</p>
                            <p className="text-sm font-semibold text-cyan-300">{feedback.confidence.toFixed(1)}%</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-400">Timestamp</p>
                            <p className="text-sm font-semibold text-gray-400">
                              {new Date(feedback.timestamp).toLocaleTimeString("pt-BR")}
                            </p>
                          </div>
                        </div>
                        {feedback.notes && (
                          <p className="text-xs text-gray-400 mt-2 italic">Nota: {feedback.notes}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </motion.div>

        {/* Botões de Exportação */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex gap-4"
        >
          <Button
            onClick={handleExportReport}
            disabled={isExporting}
            className="bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-semibold"
          >
            <Download className="w-4 h-4 mr-2" />
            {isExporting ? "Exportando..." : "Exportar Relatório JSON"}
          </Button>
          <Button
            onClick={handleExportPDF}
            disabled={isExporting}
            className="bg-purple-500 hover:bg-purple-600 text-slate-950 font-semibold"
          >
            <Download className="w-4 h-4 mr-2" />
            {isExporting ? "Gerando..." : "Gerar PDF Completo"}
          </Button>
        </motion.div>
      </div>
    </div>
  );
}
