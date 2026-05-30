import React, { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { AlertCircle, CheckCircle2, Zap, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";

interface FeedbackCorrectionProps {
  isOpen: boolean;
  onClose: () => void;
  predictedClass: string;
  confidence: number;
  imageName: string;
  classLabels: string[];
  onSubmitFeedback: (feedback: FeedbackData) => Promise<void>;
  isRetraining?: boolean;
}

export interface FeedbackData {
  imageName: string;
  predictedClass: string;
  correctClass: string;
  confidence: number;
  notes: string;
  timestamp: string;
}

export const FeedbackCorrection: React.FC<FeedbackCorrectionProps> = ({
  isOpen,
  onClose,
  predictedClass,
  confidence,
  imageName,
  classLabels,
  onSubmitFeedback,
  isRetraining = false,
}) => {
  const [correctClass, setCorrectClass] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);

  const handleSubmit = async () => {
    if (!correctClass) {
      toast.error("Por favor, selecione a classe correta");
      return;
    }

    setIsSubmitting(true);
    try {
      const feedback: FeedbackData = {
        imageName,
        predictedClass,
        correctClass,
        confidence,
        notes,
        timestamp: new Date().toISOString(),
      };

      await onSubmitFeedback(feedback);
      setShowConfirmation(true);
      
      setTimeout(() => {
        setCorrectClass("");
        setNotes("");
        setShowConfirmation(false);
        onClose();
      }, 2000);
    } catch (error) {
      toast.error("Erro ao enviar feedback");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl bg-slate-900 border-cyan-500/30">
        <DialogHeader>
          <DialogTitle className="text-cyan-400 flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            Corrigir Classificação
          </DialogTitle>
          <DialogDescription>
            Ajude-nos a melhorar o modelo informando a classificação correta
          </DialogDescription>
        </DialogHeader>

        {!showConfirmation ? (
          <div className="space-y-6 py-6">
            {/* Informações Atuais */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-slate-800/50 border border-cyan-500/20 rounded-lg p-4"
            >
              <h3 className="text-sm font-semibold text-cyan-400 mb-3">Classificação Atual</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-400">Arquivo</p>
                  <p className="text-sm font-semibold text-cyan-300 truncate">{imageName}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Classe Predita</p>
                  <p className="text-sm font-semibold text-cyan-300">{predictedClass}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Confiança</p>
                  <p className="text-sm font-semibold text-cyan-300">{confidence}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Status</p>
                  <p className="text-sm font-semibold text-red-400">❌ Incorreta</p>
                </div>
              </div>
            </motion.div>

            {/* Seleção da Classe Correta */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="space-y-3"
            >
              <label className="text-sm font-semibold text-cyan-400">
                Qual é a classe correta?
              </label>
              <Select value={correctClass} onValueChange={setCorrectClass}>
                <SelectTrigger className="bg-slate-800/50 border-cyan-500/30 text-cyan-400">
                  <SelectValue placeholder="Selecione a classe correta..." />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-cyan-500/30">
                  {classLabels.map((label) => (
                    <SelectItem key={label} value={label} className="text-cyan-300">
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </motion.div>

            {/* Notas Adicionais */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="space-y-3"
            >
              <label className="text-sm font-semibold text-cyan-400">
                Notas Adicionais (Opcional)
              </label>
              <Textarea
                placeholder="Descreva por que a classificação estava errada ou adicione observações clínicas..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="bg-slate-800/50 border-cyan-500/30 text-cyan-300 placeholder:text-gray-500 min-h-24"
              />
            </motion.div>

            {/* Informações sobre Retreinamento */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-4"
            >
              <div className="flex gap-3">
                <Zap className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-cyan-400">Retreinamento Automático</p>
                  <p className="text-xs text-gray-400">
                    Após 5+ correções, o modelo será automaticamente retreinado com Quantum Nexus PhD usando:
                  </p>
                  <ul className="text-xs text-gray-400 space-y-1 mt-2 ml-4">
                    <li>✓ Validação Cruzada 5-Fold com estratificação</li>
                    <li>✓ Bootstrap 1000 iterações (IC 95%)</li>
                    <li>✓ Testes Estatísticos (McNemar, Cochran Q)</li>
                    <li>✓ Mitigação de Erros Híbrida (ZNE+PEC)</li>
                    <li>✓ Análise de Robustez e Calibração</li>
                  </ul>
                </div>
              </div>
            </motion.div>

            {/* Botões de Ação */}
            <div className="flex gap-3 pt-4">
              <Button
                variant="outline"
                onClick={onClose}
                className="flex-1 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
              >
                Cancelar
              </Button>
              <Button
                onClick={handleSubmit}
                disabled={!correctClass || isSubmitting || isRetraining}
                className="flex-1 bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-semibold"
              >
                {isSubmitting ? "Enviando..." : "Enviar Correção"}
              </Button>
            </div>
          </div>
        ) : (
          /* Confirmation Screen */
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="py-12 text-center space-y-4"
          >
            <CheckCircle2 className="w-16 h-16 text-green-400 mx-auto" />
            <div>
              <h3 className="text-lg font-bold text-cyan-400 mb-2">Feedback Registrado!</h3>
              <p className="text-sm text-gray-400">
                Obrigado por ajudar a melhorar o modelo. Sua correção foi salva com sucesso.
              </p>
            </div>
            <div className="bg-slate-800/50 border border-green-500/30 rounded-lg p-3 mt-4">
              <p className="text-xs text-gray-400 mb-2">Próximas correções para retreinamento:</p>
              <div className="flex gap-1 justify-center">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-xs font-bold text-cyan-400"
                  >
                    {i}
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </DialogContent>
    </Dialog>
  );
};
