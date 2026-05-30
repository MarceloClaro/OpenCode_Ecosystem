import { useState, useCallback } from "react";

export interface AnalysisResponse {
  status: "success" | "error";
  predicted_class?: string;
  confidence?: number;
  probabilities?: Array<{ class: string; probability: number }>;
  inference_time?: number;
  gradcam?: string;
  model_version?: string;
  error?: string;
}

export const useQMLAnalysis = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeImage = useCallback(async (imageBase64: string): Promise<AnalysisResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      // Chamar serviço QML real via API
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image: imageBase64,
        }),
      });

      if (!response.ok) {
        throw new Error(`Erro na análise: ${response.statusText}`);
      }

      const data: AnalysisResponse = await response.json();
      
      if (data.status === "error") {
        setError(data.error || "Erro desconhecido");
        return data;
      }

      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao analisar imagem";
      setError(errorMessage);
      return { status: "error", error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const submitFeedback = useCallback(async (feedback: {
    imageName: string;
    predictedClass: string;
    correctClass: string;
    confidence: number;
    notes: string;
  }) => {
    try {
      const response = await fetch("/api/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(feedback),
      });

      if (!response.ok) {
        throw new Error("Erro ao enviar feedback");
      }

      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao enviar feedback";
      setError(errorMessage);
      throw err;
    }
  }, []);

  const retrain = useCallback(async () => {
    try {
      const response = await fetch("/api/retrain", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Erro ao iniciar retreinamento");
      }

      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao retreinar";
      setError(errorMessage);
      throw err;
    }
  }, []);

  return {
    analyzeImage,
    submitFeedback,
    retrain,
    isLoading,
    error,
  };
};
