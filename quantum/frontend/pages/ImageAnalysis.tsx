import React, { useState, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, X, Download, BarChart3, Zap, Clock, Target } from "lucide-react";
import { motion } from "framer-motion";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from "recharts";
import { toast } from "sonner";

// Dados de exemplo para classes
const classLabels = ["MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC"];
const classNames = [
  "Melanoma",
  "Nevo",
  "Carcinoma Basocelular",
  "Ceratose Actínica",
  "Ceratose Benigna",
  "Dermatofibroma",
  "Lesão Vascular"
];

const classColors = ["#ef4444", "#8b5cf6", "#f59e0b", "#ec4899", "#06b6d4", "#10b981", "#3b82f6"];

interface AnalysisResult {
  id: string;
  timestamp: string;
  imageName: string;
  imageUrl: string;
  predictedClass: string;
  confidence: number;
  probabilities: { class: string; probability: number }[];
  inferenceTime: number;
  gradcamUrl?: string;
}

export default function ImageAnalysis() {
  const [uploadedImage, setUploadedImage] = useState<string>("");
  const [imageName, setImageName] = useState<string>("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [history, setHistory] = useState<AnalysisResult[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Simular classificação QML
  const simulateQMLClassification = async (imageData: string) => {
    setIsAnalyzing(true);
    
    // Simular tempo de inferência
    const startTime = performance.now();
    
    // Simular delay de processamento
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const endTime = performance.now();
    const inferenceTime = (endTime - startTime) / 1000;

    // Gerar probabilidades aleatórias realistas
    const baseProbs = [
      Math.random() * 0.3,
      Math.random() * 0.3,
      Math.random() * 0.2,
      Math.random() * 0.1,
      Math.random() * 0.05,
      Math.random() * 0.02,
      Math.random() * 0.03,
    ];

    const totalProb = baseProbs.reduce((a, b) => a + b, 0);
    const normalizedProbs = baseProbs.map(p => p / totalProb);

    // Encontrar classe com maior probabilidade
    const maxIndex = normalizedProbs.indexOf(Math.max(...normalizedProbs));
    const predictedClass = classLabels[maxIndex];
    const confidence = normalizedProbs[maxIndex];

    // Criar dados de probabilidades
    const probabilities = classLabels.map((label, idx) => ({
      class: label,
      probability: parseFloat((normalizedProbs[idx] * 100).toFixed(2))
    }));

    const result: AnalysisResult = {
      id: `analysis_${Date.now()}`,
      timestamp: new Date().toLocaleString("pt-BR"),
      imageName,
      imageUrl: uploadedImage!,
      predictedClass,
      confidence: parseFloat((confidence * 100).toFixed(2)),
      probabilities,
      inferenceTime: parseFloat(inferenceTime.toFixed(3)),
      gradcamUrl: URL.createObjectURL(
        new Blob([`<svg viewBox="0 0 224 224"><defs><linearGradient id="grad"><stop offset="0%" style="stop-color:rgb(255,0,0);stop-opacity:0.3" /><stop offset="100%" style="stop-color:rgb(255,255,0);stop-opacity:0.8" /></linearGradient></defs><rect width="224" height="224" fill="url(#grad)"/></svg>`], { type: "image/svg+xml" })
      )
    };

    setAnalysisResult(result);
    setHistory([result, ...history.slice(0, 9)]);
    setIsAnalyzing(false);
    toast.success("Análise concluída com sucesso!");
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      processFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      processFile(files[0]);
    }
  };

  const processFile = (file: File) => {
    if (!file.type.startsWith("image/")) {
      toast.error("Por favor, selecione um arquivo de imagem válido");
      return;
    }

    setImageName(file.name);
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      setUploadedImage(result);
      setAnalysisResult(null);
    };
    reader.readAsDataURL(file);
  };

  const handleAnalyze = async () => {
    if (!uploadedImage) {
      toast.error("Por favor, selecione uma imagem primeiro");
      return;
    }
    await simulateQMLClassification(uploadedImage);
  };

  const handleClearImage = () => {
    setUploadedImage("");
    setImageName("");
    setAnalysisResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDownloadResult = () => {
    if (!analysisResult) return;
    
    const resultText = `
RESULTADO DA ANÁLISE QML
========================
Data: ${analysisResult.timestamp}
Arquivo: ${analysisResult.imageName}

CLASSIFICAÇÃO
Classe Predita: ${analysisResult.predictedClass} (${classNames[classLabels.indexOf(analysisResult.predictedClass)]})
Confiança: ${analysisResult.confidence}%
Tempo de Inferência: ${analysisResult.inferenceTime}s

PROBABILIDADES POR CLASSE
${analysisResult.probabilities.map(p => `${p.class}: ${p.probability}%`).join("\n")}
    `.trim();

    const blob = new Blob([resultText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `analise_qml_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-cyan-400 flex items-center gap-3 mb-2">
            <Zap className="w-10 h-10" />
            Análise de Imagem Médica
          </h1>
          <p className="text-gray-400">Envie uma imagem de lesão de pele para classificação QML com Grad-CAM</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Upload Section */}
          <div className="lg:col-span-1">
            <Card className="bg-slate-800/50 border-cyan-500/20 h-full">
              <CardHeader>
                <CardTitle className="text-cyan-400">Enviar Imagem</CardTitle>
                <CardDescription>Arraste ou clique para selecionar</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Upload Area */}
                <motion.div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all ${
                    dragActive
                      ? "border-cyan-400 bg-cyan-500/10"
                      : "border-cyan-500/30 bg-slate-700/20 hover:border-cyan-400/50"
                  }`}
                  whileHover={{ scale: 1.02 }}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full"
                  >
                    <Upload className="w-8 h-8 mx-auto mb-2 text-cyan-400" />
                    <p className="text-sm font-semibold text-cyan-400">Clique ou arraste</p>
                    <p className="text-xs text-gray-400 mt-1">PNG, JPG, GIF até 10MB</p>
                  </button>
                </motion.div>

                {/* Preview */}
                {uploadedImage.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="space-y-3"
                  >
                    <div className="relative bg-slate-700/30 rounded-lg overflow-hidden border border-cyan-500/20">
                      <img
                        src={uploadedImage}
                        alt="Preview"
                        className="w-full h-auto"
                      />
                    </div>
                    <p className="text-xs text-gray-400 truncate">{imageName}</p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleClearImage}
                      className="w-full border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
                    >
                      <X className="w-4 h-4 mr-2" />
                      Limpar
                    </Button>
                  </motion.div>
                )}

                {/* Analyze Button */}
                <Button
                  onClick={handleAnalyze}
                  disabled={uploadedImage.length === 0 || isAnalyzing}
                  className="w-full bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-semibold"
                >
                  {isAnalyzing ? "Analisando..." : "Analisar Imagem"}
                </Button>

                {isAnalyzing && (
                  <div className="space-y-2">
                    <Progress value={65} className="h-2" />
                    <p className="text-xs text-gray-400 text-center">Processando com QML...</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Results Section */}
          <div className="lg:col-span-2 space-y-6">
            {analysisResult ? (
              <>
                {/* Classification Result */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Card className="bg-slate-800/50 border-cyan-500/20">
                    <CardHeader>
                      <CardTitle className="text-cyan-400">Resultado da Classificação</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {/* Main Result */}
                      <div className="bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/30 rounded-lg p-6">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-xs text-gray-400 mb-1">Classe Predita</p>
                            <p className="text-2xl font-bold text-cyan-400">
                              {analysisResult.predictedClass}
                            </p>
                            <p className="text-xs text-gray-400 mt-1">
                              {classNames[classLabels.indexOf(analysisResult.predictedClass)]}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-400 mb-1">Confiança</p>
                            <p className="text-2xl font-bold text-cyan-400">
                              {analysisResult.confidence}%
                            </p>
                            <Progress
                              value={analysisResult.confidence}
                              className="mt-2 h-2"
                            />
                          </div>
                        </div>
                      </div>

                      {/* Metrics */}
                      <div className="grid grid-cols-3 gap-3">
                        <div className="bg-slate-700/30 border border-cyan-500/20 rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <Clock className="w-4 h-4 text-cyan-400" />
                            <p className="text-xs text-gray-400">Tempo</p>
                          </div>
                          <p className="text-lg font-bold text-cyan-400">
                            {analysisResult.inferenceTime}s
                          </p>
                        </div>
                        <div className="bg-slate-700/30 border border-cyan-500/20 rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <Target className="w-4 h-4 text-cyan-400" />
                            <p className="text-xs text-gray-400">Precisão</p>
                          </div>
                          <p className="text-lg font-bold text-cyan-400">
                            {(analysisResult.confidence * 0.95).toFixed(1)}%
                          </p>
                        </div>
                        <div className="bg-slate-700/30 border border-cyan-500/20 rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <BarChart3 className="w-4 h-4 text-cyan-400" />
                            <p className="text-xs text-gray-400">Modelo</p>
                          </div>
                          <p className="text-lg font-bold text-cyan-400">
                            QML v1.0
                          </p>
                        </div>
                      </div>

                      {/* Download Button */}
                      <Button
                        onClick={handleDownloadResult}
                        className="w-full bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-semibold"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Baixar Resultado
                      </Button>
                    </CardContent>
                  </Card>
                </motion.div>

                {/* Tabs for Details */}
                <Tabs defaultValue="probabilidades" className="w-full">
                  <TabsList className="grid w-full grid-cols-3 bg-slate-800/50 border border-cyan-500/20">
                    <TabsTrigger value="probabilidades" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
                      Probabilidades
                    </TabsTrigger>
                    <TabsTrigger value="gradcam" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
                      Grad-CAM
                    </TabsTrigger>
                    <TabsTrigger value="detalhes" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
                      Detalhes
                    </TabsTrigger>
                  </TabsList>

                  {/* Probabilidades Tab */}
                  <TabsContent value="probabilidades">
                    <Card className="bg-slate-800/50 border-cyan-500/20">
                      <CardHeader>
                        <CardTitle className="text-cyan-400">Distribuição de Probabilidades</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-6">
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={analysisResult.probabilities}>
                            <CartesianGrid stroke="#334155" />
                            <XAxis dataKey="class" stroke="#94a3b8" />
                            <YAxis stroke="#94a3b8" label={{ value: "Probabilidade (%)", angle: -90, position: "insideLeft" }} />
                            <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #00d9ff" }} />
                            <Bar dataKey="probability" fill="#00d9ff" />
                          </BarChart>
                        </ResponsiveContainer>

                        {/* Probability List */}
                        <div className="space-y-2">
                          {analysisResult.probabilities
                            .sort((a, b) => b.probability - a.probability)
                            .map((item, idx) => (
                              <div key={item.class} className="flex items-center justify-between p-2 bg-slate-700/30 rounded border border-cyan-500/20">
                                <div className="flex items-center gap-2">
                                  <div
                                    className="w-3 h-3 rounded-full"
                                    style={{ backgroundColor: classColors[classLabels.indexOf(item.class)] }}
                                  />
                                  <span className="text-sm font-semibold text-cyan-400">{item.class}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Progress value={item.probability} className="w-24 h-2" />
                                  <span className="text-sm font-bold text-cyan-400 w-12 text-right">
                                    {item.probability}%
                                  </span>
                                </div>
                              </div>
                            ))}
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  {/* Grad-CAM Tab */}
                  <TabsContent value="gradcam">
                    <Card className="bg-slate-800/50 border-cyan-500/20">
                      <CardHeader>
                        <CardTitle className="text-cyan-400">Visualização Grad-CAM</CardTitle>
                        <CardDescription>Regiões críticas que influenciaram a classificação</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="relative bg-slate-700/30 rounded-lg overflow-hidden border border-cyan-500/20">
                          <img
                            src={uploadedImage}
                            alt="Original"
                            className="w-full h-auto opacity-60"
                          />
                          <div className="absolute inset-0 bg-gradient-to-br from-red-500/30 via-yellow-500/20 to-transparent mix-blend-overlay" />
                        </div>
                        <p className="text-xs text-gray-400">
                          O mapa de calor vermelho/amarelo indica as regiões que o modelo considerou mais importantes para a classificação.
                        </p>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  {/* Detalhes Tab */}
                  <TabsContent value="detalhes">
                    <Card className="bg-slate-800/50 border-cyan-500/20">
                      <CardHeader>
                        <CardTitle className="text-cyan-400">Detalhes da Análise</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="grid grid-cols-2 gap-3">
                          <div className="bg-slate-700/30 p-3 rounded border border-cyan-500/20">
                            <p className="text-xs text-gray-400">Data/Hora</p>
                            <p className="text-sm font-semibold text-cyan-400">{analysisResult.timestamp}</p>
                          </div>
                          <div className="bg-slate-700/30 p-3 rounded border border-cyan-500/20">
                            <p className="text-xs text-gray-400">Arquivo</p>
                            <p className="text-sm font-semibold text-cyan-400 truncate">{analysisResult.imageName}</p>
                          </div>
                          <div className="bg-slate-700/30 p-3 rounded border border-cyan-500/20">
                            <p className="text-xs text-gray-400">Tempo de Inferência</p>
                            <p className="text-sm font-semibold text-cyan-400">{analysisResult.inferenceTime}s</p>
                          </div>
                          <div className="bg-slate-700/30 p-3 rounded border border-cyan-500/20">
                            <p className="text-xs text-gray-400">ID da Análise</p>
                            <p className="text-sm font-semibold text-cyan-400 truncate">{analysisResult.id}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>
                </Tabs>
              </>
            ) : (
              <Card className="bg-slate-800/50 border-cyan-500/20 lg:col-span-2">
                <CardContent className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <Zap className="w-12 h-12 text-cyan-400/50 mx-auto mb-3" />
                    <p className="text-gray-400">Envie uma imagem para começar a análise</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* History Section */}
        {history.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8"
          >
            <Card className="bg-slate-800/50 border-cyan-500/20">
              <CardHeader>
                <CardTitle className="text-cyan-400">Histórico de Análises</CardTitle>
                <CardDescription>Últimas {history.length} análises realizadas</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {history.map((item, idx) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="flex items-center justify-between p-3 bg-slate-700/30 border border-cyan-500/20 rounded-lg hover:bg-slate-700/50 transition-all cursor-pointer"
                      onClick={() => {
                        setUploadedImage(item.imageUrl);
                        setImageName(item.imageName);
                        setAnalysisResult(item);
                      }}
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <img
                          src={item.imageUrl}
                          alt={item.imageName}
                          className="w-10 h-10 rounded object-cover"
                        />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-cyan-400 truncate">{item.imageName}</p>
                          <p className="text-xs text-gray-400">{item.timestamp}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <p className="text-sm font-bold text-cyan-400">{item.predictedClass}</p>
                          <p className="text-xs text-gray-400">{item.confidence}%</p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
}
