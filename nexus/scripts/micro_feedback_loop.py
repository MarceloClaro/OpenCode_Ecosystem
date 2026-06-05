# -*- coding: utf-8 -*-
# SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
# Toda resposta ao usuário DEVE ser em português do Brasil formal.
# Contexto em chinês para eficiência de tokens (densidade +40%%).
# Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)

"""
TMA v5.0 MICRO - Micro Feedback Loop
Feedback granular por operação com lições e melhoria contínua
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
from datetime import datetime


class FeedbackType(Enum):
    """Tipos de feedback"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    WARNING = "warning"
    OPTIMIZATION = "optimization"


@dataclass
class Lesson:
    """Lição extraída de uma operação"""
    barrier_id: str
    lesson_type: str  # "success", "failure", "optimization"
    description: str
    impact: float  # 0-1 (impacto na próxima iteração)
    confidence: float  # 0-1 (confiança na lição)
    applicable_to: List[str]  # barriers onde é aplicável
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            "barrier_id": self.barrier_id,
            "lesson_type": self.lesson_type,
            "description": self.description,
            "impact": self.impact,
            "confidence": self.confidence,
            "applicable_to": self.applicable_to,
            "timestamp": self.timestamp
        }


@dataclass
class OperationFeedback:
    """Feedback de uma operação atômica"""
    barrier_id: str
    operation_name: str
    feedback_type: FeedbackType
    success: bool
    execution_time_ms: float
    quality_score: float  # 0-1
    confidence: float  # 0-1
    error_message: Optional[str] = None
    lessons: List[Lesson] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            "barrier_id": self.barrier_id,
            "operation_name": self.operation_name,
            "feedback_type": self.feedback_type.value,
            "success": self.success,
            "execution_time_ms": self.execution_time_ms,
            "quality_score": self.quality_score,
            "confidence": self.confidence,
            "error_message": self.error_message,
            "lessons": [l.to_dict() for l in self.lessons],
            "metrics": self.metrics,
            "timestamp": self.timestamp
        }


class MicroFeedbackEngine:
    """Motor de feedback granular com 120 feedback points"""
    
    def __init__(self):
        self.feedback_history: List[OperationFeedback] = []
        self.lessons_database: List[Lesson] = []
        self.barrier_metrics: Dict[str, Dict] = {}
        self.improvement_tracking: Dict[str, List[float]] = {}
    
    def record_feedback(
        self,
        barrier_id: str,
        operation_name: str,
        success: bool,
        execution_time_ms: float,
        quality_score: float,
        confidence: float,
        error_message: Optional[str] = None,
        metrics: Optional[Dict] = None
    ) -> OperationFeedback:
        """Registra feedback de uma operação"""
        
        # Determinar tipo de feedback
        if success and quality_score >= 0.9:
            feedback_type = FeedbackType.SUCCESS
        elif success and quality_score >= 0.7:
            feedback_type = FeedbackType.PARTIAL_SUCCESS
        elif not success:
            feedback_type = FeedbackType.FAILURE
        else:
            feedback_type = FeedbackType.WARNING
        
        # Criar feedback
        feedback = OperationFeedback(
            barrier_id=barrier_id,
            operation_name=operation_name,
            feedback_type=feedback_type,
            success=success,
            execution_time_ms=execution_time_ms,
            quality_score=quality_score,
            confidence=confidence,
            error_message=error_message,
            metrics=metrics or {}
        )
        
        # Extrair lições
        lessons = self._extract_lessons(feedback)
        feedback.lessons = lessons
        
        # Registrar
        self.feedback_history.append(feedback)
        self.lessons_database.extend(lessons)
        
        # Atualizar métricas
        self._update_barrier_metrics(barrier_id, feedback)
        self._update_improvement_tracking(barrier_id, quality_score)
        
        return feedback
    
    def _extract_lessons(self, feedback: OperationFeedback) -> List[Lesson]:
        """Extrai lições de um feedback"""
        lessons = []
        
        # Lição 1: Sucesso
        if feedback.success and feedback.quality_score >= 0.9:
            lessons.append(Lesson(
                barrier_id=feedback.barrier_id,
                lesson_type="success",
                description=f"Operação {feedback.operation_name} completada com sucesso",
                impact=0.1,  # Pequeno impacto (já está funcionando)
                confidence=feedback.confidence,
                applicable_to=[feedback.barrier_id]
            ))
        
        # Lição 2: Falha
        elif not feedback.success:
            lessons.append(Lesson(
                barrier_id=feedback.barrier_id,
                lesson_type="failure",
                description=f"Falha em {feedback.operation_name}: {feedback.error_message}",
                impact=0.8,  # Alto impacto (deve ser evitado)
                confidence=feedback.confidence,
                applicable_to=[feedback.barrier_id]
            ))
        
        # Lição 3: Otimização
        if feedback.execution_time_ms > 5000:  # Mais de 5 segundos
            lessons.append(Lesson(
                barrier_id=feedback.barrier_id,
                lesson_type="optimization",
                description=f"Operação {feedback.operation_name} lenta ({feedback.execution_time_ms:.0f}ms)",
                impact=0.5,  # Médio impacto (pode ser otimizado)
                confidence=0.7,
                applicable_to=[feedback.barrier_id]
            ))
        
        # Lição 4: Qualidade
        if feedback.quality_score < 0.7:
            lessons.append(Lesson(
                barrier_id=feedback.barrier_id,
                lesson_type="optimization",
                description=f"Qualidade baixa ({feedback.quality_score:.1f}) em {feedback.operation_name}",
                impact=0.7,  # Alto impacto (deve melhorar)
                confidence=feedback.confidence,
                applicable_to=[feedback.barrier_id]
            ))
        
        return lessons
    
    def _update_barrier_metrics(self, barrier_id: str, feedback: OperationFeedback):
        """Atualiza métricas do barrier"""
        if barrier_id not in self.barrier_metrics:
            self.barrier_metrics[barrier_id] = {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "avg_quality": 0.0,
                "avg_execution_time": 0.0,
                "avg_confidence": 0.0
            }
        
        metrics = self.barrier_metrics[barrier_id]
        metrics["total_executions"] += 1
        
        if feedback.success:
            metrics["successful"] += 1
        else:
            metrics["failed"] += 1
        
        # Atualizar médias (média móvel)
        n = metrics["total_executions"]
        metrics["avg_quality"] = (metrics["avg_quality"] * (n - 1) + feedback.quality_score) / n
        metrics["avg_execution_time"] = (metrics["avg_execution_time"] * (n - 1) + feedback.execution_time_ms) / n
        metrics["avg_confidence"] = (metrics["avg_confidence"] * (n - 1) + feedback.confidence) / n
    
    def _update_improvement_tracking(self, barrier_id: str, quality_score: float):
        """Rastreia melhoria ao longo do tempo"""
        if barrier_id not in self.improvement_tracking:
            self.improvement_tracking[barrier_id] = []
        
        self.improvement_tracking[barrier_id].append(quality_score)
    
    def get_barrier_feedback(self, barrier_id: str) -> List[OperationFeedback]:
        """Retorna feedback de um barrier"""
        return [f for f in self.feedback_history if f.barrier_id == barrier_id]
    
    def get_barrier_lessons(self, barrier_id: str) -> List[Lesson]:
        """Retorna lições de um barrier"""
        return [l for l in self.lessons_database if l.barrier_id == barrier_id]
    
    def get_barrier_metrics(self, barrier_id: str) -> Dict:
        """Retorna métricas de um barrier"""
        return self.barrier_metrics.get(barrier_id, {})
    
    def get_improvement_trend(self, barrier_id: str) -> Tuple[float, float]:
        """Retorna tendência de melhoria (slope, R²)"""
        if barrier_id not in self.improvement_tracking:
            return 0.0, 0.0
        
        scores = self.improvement_tracking[barrier_id]
        if len(scores) < 2:
            return 0.0, 0.0
        
        # Calcular slope (melhoria)
        n = len(scores)
        x_mean = (n - 1) / 2
        y_mean = sum(scores) / n
        
        numerator = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0.0
        
        # Calcular R² (qualidade do ajuste)
        ss_res = sum((scores[i] - (slope * i + (y_mean - slope * x_mean))) ** 2 for i in range(n))
        ss_tot = sum((scores[i] - y_mean) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        
        return slope, r_squared
    
    def get_top_lessons(self, limit: int = 10) -> List[Lesson]:
        """Retorna lições com maior impacto"""
        sorted_lessons = sorted(
            self.lessons_database,
            key=lambda l: l.impact * l.confidence,
            reverse=True
        )
        return sorted_lessons[:limit]
    
    def get_applicable_lessons(self, barrier_id: str) -> List[Lesson]:
        """Retorna lições aplicáveis a um barrier"""
        applicable = []
        for lesson in self.lessons_database:
            if barrier_id in lesson.applicable_to or barrier_id.split('.')[0] in lesson.applicable_to:
                applicable.append(lesson)
        
        return sorted(applicable, key=lambda l: l.impact * l.confidence, reverse=True)
    
    def generate_feedback_report(self, barrier_id: Optional[str] = None) -> str:
        """Gera relatório de feedback"""
        if barrier_id:
            feedback_list = self.get_barrier_feedback(barrier_id)
            metrics = self.get_barrier_metrics(barrier_id)
            lessons = self.get_barrier_lessons(barrier_id)
            improvement = self.get_improvement_trend(barrier_id)
            
            report = f"""
╔════════════════════════════════════════════════════════════════╗
║           MICRO FEEDBACK REPORT - {barrier_id}
╚════════════════════════════════════════════════════════════════╝

Executions: {len(feedback_list)}
Success Rate: {metrics.get('successful', 0) / max(metrics.get('total_executions', 1), 1):.1%}
Avg Quality: {metrics.get('avg_quality', 0):.2f}
Avg Execution Time: {metrics.get('avg_execution_time', 0):.0f}ms
Avg Confidence: {metrics.get('avg_confidence', 0):.2f}

Improvement Trend:
  Slope: {improvement[0]:.4f} (per execution)
  R²: {improvement[1]:.4f}

Lessons Extracted: {len(lessons)}
"""
            
            for i, lesson in enumerate(lessons[:5], 1):
                report += f"\n  {i}. {lesson.description}"
                report += f"\n     Impact: {lesson.impact:.1f}, Confidence: {lesson.confidence:.1f}"
            
            return report
        
        else:
            # Relatório geral
            report = f"""
╔════════════════════════════════════════════════════════════════╗
║           MICRO FEEDBACK REPORT - GENERAL
╚════════════════════════════════════════════════════════════════╝

Total Feedback Records: {len(self.feedback_history)}
Total Lessons Extracted: {len(self.lessons_database)}
Barriers Tracked: {len(self.barrier_metrics)}

Top Lessons:
"""
            
            top_lessons = self.get_top_lessons(5)
            for i, lesson in enumerate(top_lessons, 1):
                report += f"\n  {i}. [{lesson.barrier_id}] {lesson.description}"
                report += f"\n     Impact: {lesson.impact:.1f}, Confidence: {lesson.confidence:.1f}"
            
            return report
    
    def export_feedback_as_json(self, barrier_id: Optional[str] = None) -> str:
        """Exporta feedback como JSON"""
        if barrier_id:
            feedback_list = self.get_barrier_feedback(barrier_id)
        else:
            feedback_list = self.feedback_history
        
        data = {
            "feedback": [f.to_dict() for f in feedback_list],
            "count": len(feedback_list),
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(data, indent=2)


# Exemplo de uso
if __name__ == "__main__":
    engine = MicroFeedbackEngine()
    
    # Registrar feedback
    feedback1 = engine.record_feedback(
        barrier_id="SB1.1",
        operation_name="Concept Extraction",
        success=True,
        execution_time_ms=2500,
        quality_score=0.92,
        confidence=0.88,
        metrics={"concepts_extracted": 45}
    )
    
    feedback2 = engine.record_feedback(
        barrier_id="SB1.1",
        operation_name="Concept Extraction",
        success=True,
        execution_time_ms=2300,
        quality_score=0.95,
        confidence=0.92,
        metrics={"concepts_extracted": 48}
    )
    
    feedback3 = engine.record_feedback(
        barrier_id="SB1.1",
        operation_name="Concept Extraction",
        success=False,
        execution_time_ms=3000,
        quality_score=0.65,
        confidence=0.70,
        error_message="Timeout during extraction",
        metrics={"concepts_extracted": 30}
    )
    
    # Relatório
    print(engine.generate_feedback_report("SB1.1"))
    print("\n" + engine.generate_feedback_report())
