"""
EvalLab Framework -- Infraestrutura para experimentos controlados A/B.

Suporta analise estatistica (t-test, Cohen's d), metricas automatizadas,
e reprodutibilidade via configuracao declarativa.
Integra-se com: SWE Evaluator, CORA-Eval, PermissionTiers.
"""

import json
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path
from typing import Optional


@dataclass
class ExperimentConfig:
    experiment_id: str
    name: str
    hypothesis: str
    condition_a: dict
    condition_b: dict
    tasks: list[str]
    repetitions: int = 10
    metrics: list[str] = field(default_factory=lambda: [
        "defect_rate", "time_to_complete", "token_cost",
        "spec_fidelity", "correction_loops", "arch_violations"
    ])
    statistical_tests: list[str] = field(default_factory=lambda: ["t_test", "cohens_d"])


@dataclass
class MetricSnapshot:
    metric_name: str
    condition: str
    values: list[float] = field(default_factory=list)

    @property
    def mean(self) -> float:
        return statistics.mean(self.values) if self.values else 0.0

    @property
    def stdev(self) -> float:
        return statistics.stdev(self.values) if len(self.values) > 1 else 0.0

    @property
    def median(self) -> float:
        return statistics.median(self.values) if self.values else 0.0


@dataclass
class StatisticalResult:
    metric_name: str
    t_statistic: float = 0.0
    p_value: float = 0.0
    cohens_d: float = 0.0
    mean_a: float = 0.0
    mean_b: float = 0.0
    stdev_a: float = 0.0
    stdev_b: float = 0.0
    significant: bool = False
    effect_size_label: str = ""


@dataclass
class ExperimentResult:
    config: ExperimentConfig
    condition_a: dict[str, MetricSnapshot] = field(default_factory=dict)
    condition_b: dict[str, MetricSnapshot] = field(default_factory=dict)
    statistical_results: list[StatisticalResult] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        significant = sum(1 for r in self.statistical_results if r.significant)
        total = len(self.statistical_results)
        return f"{significant}/{total} metricas com diferenca significativa"


class StatisticalAnalyzer:
    """Analise estatistica para experimentos controlados."""

    @staticmethod
    def t_test(values_a: list[float], values_b: list[float]) -> tuple[float, float]:
        """Teste t de Student para duas amostras independentes (Welch)."""
        n_a, n_b = len(values_a), len(values_b)
        if n_a < 2 or n_b < 2:
            return 0.0, 1.0

        mean_a = statistics.mean(values_a)
        mean_b = statistics.mean(values_b)
        var_a = statistics.variance(values_a)
        var_b = statistics.variance(values_b)

        se = sqrt(var_a / n_a + var_b / n_b)
        if se == 0:
            return 0.0, 1.0

        t_stat = (mean_a - mean_b) / se

        df_num = (var_a / n_a + var_b / n_b) ** 2
        df_den = ((var_a / n_a) ** 2) / (n_a - 1) + ((var_b / n_b) ** 2) / (n_b - 1)
        df = df_num / df_den if df_den > 0 else n_a + n_b - 2

        p_value = StatisticalAnalyzer._t_distribution_pvalue(abs(t_stat), df)
        return round(t_stat, 4), round(p_value, 4)

    @staticmethod
    def cohens_d(values_a: list[float], values_b: list[float]) -> float:
        """Tamanho de efeito de Cohen."""
        n_a, n_b = len(values_a), len(values_b)
        if n_a < 2 or n_b < 2:
            return 0.0

        mean_a = statistics.mean(values_a)
        mean_b = statistics.mean(values_b)
        var_a = statistics.variance(values_a)
        var_b = statistics.variance(values_b)

        pooled_sd = sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))
        if pooled_sd == 0:
            return 0.0

        return round(abs(mean_a - mean_b) / pooled_sd, 4)

    @staticmethod
    def effect_size_label(d: float) -> str:
        if d < 0.2: return "desprezivel"
        if d < 0.5: return "pequeno"
        if d < 0.8: return "medio"
        return "grande"

    @staticmethod
    def _t_distribution_pvalue(t: float, df: float) -> float:
        """Aproximacao da CDF da distribuicao t."""
        if df <= 0:
            return 1.0
        x = df / (df + t * t)
        a = 0.5 * StatisticalAnalyzer._betainc(df / 2, 0.5, x)
        return round(a, 4) if a > 0 else 0.0001

    @staticmethod
    def _betainc(a: float, b: float, x: float, steps: int = 1000) -> float:
        """Aproximacao numerica da funcao beta incompleta."""
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        result = 0.0
        for i in range(steps):
            t_val = (i + 0.5) / steps * x
            result += (t_val ** (a - 1)) * ((1 - t_val) ** (b - 1))
        result *= x / steps
        from math import gamma
        return result * gamma(a + b) / (gamma(a) * gamma(b))


class EvalLab:
    """Framework de experimentacao controlada."""

    def __init__(self, output_dir: str = "eval_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.analyzer = StatisticalAnalyzer()
        self.experiments: list[ExperimentResult] = []

    def run_experiment(self, config: ExperimentConfig,
                       runner_a, runner_b,
                       data_dir: str) -> ExperimentResult:
        """Executa experimento A/B com metricas automatizadas."""
        result = ExperimentResult(
            config=config,
            started_at=datetime.now(timezone.utc).isoformat()
        )

        for metric_name in config.metrics:
            result.condition_a[metric_name] = MetricSnapshot(
                metric_name=metric_name, condition="A"
            )
            result.condition_b[metric_name] = MetricSnapshot(
                metric_name=metric_name, condition="B"
            )

        for rep in range(config.repetitions):
            for task_id in config.tasks:
                a_metrics = self._run_condition(
                    runner_a, config.condition_a, task_id, rep, data_dir
                )
                for k, v in a_metrics.items():
                    if k in result.condition_a:
                        result.condition_a[k].values.append(v)

                b_metrics = self._run_condition(
                    runner_b, config.condition_b, task_id, rep, data_dir
                )
                for k, v in b_metrics.items():
                    if k in result.condition_b:
                        result.condition_b[k].values.append(v)

        result.statistical_results = self._compute_statistics(result)
        result.completed_at = datetime.now(timezone.utc).isoformat()
        self.experiments.append(result)
        self._save_result(result)
        return result

    def _run_condition(self, runner, condition_config: dict,
                       task_id: str, rep: int, data_dir: str) -> dict:
        """Executa uma condicao e coleta metricas."""
        start = time.time()
        try:
            output = runner(task_id=task_id, repetition=rep,
                          config=condition_config, data_dir=data_dir)
            elapsed = time.time() - start
            return {
                "time_to_complete": elapsed,
                "defect_rate": output.get("defect_rate", 0),
                "token_cost": output.get("token_cost", 0),
                "spec_fidelity": output.get("spec_fidelity", 100),
                "correction_loops": output.get("correction_loops", 0),
                "arch_violations": output.get("arch_violations", 0),
            }
        except Exception as e:
            return {
                "time_to_complete": time.time() - start,
                "defect_rate": 100,
                "token_cost": 0,
                "spec_fidelity": 0,
                "correction_loops": 99,
                "arch_violations": 99,
            }

    def _compute_statistics(self, result: ExperimentResult) -> list[StatisticalResult]:
        stats = []
        for metric_name in result.config.metrics:
            values_a = result.condition_a.get(metric_name, MetricSnapshot(metric_name, "A")).values
            values_b = result.condition_b.get(metric_name, MetricSnapshot(metric_name, "B")).values

            if len(values_a) < 2 or len(values_b) < 2:
                continue

            t_stat, p_value = self.analyzer.t_test(values_a, values_b)
            d = self.analyzer.cohens_d(values_a, values_b)

            stats.append(StatisticalResult(
                metric_name=metric_name,
                t_statistic=t_stat,
                p_value=p_value,
                cohens_d=d,
                mean_a=statistics.mean(values_a),
                mean_b=statistics.mean(values_b),
                stdev_a=statistics.stdev(values_a) if len(values_a) > 1 else 0,
                stdev_b=statistics.stdev(values_b) if len(values_b) > 1 else 0,
                significant=p_value < 0.05 / len(result.config.metrics),
                effect_size_label=self.analyzer.effect_size_label(d)
            ))

        return stats

    def compare_experiments(self, exp_id_1: str, exp_id_2: str) -> Optional[dict]:
        exp1 = next((e for e in self.experiments if e.config.experiment_id == exp_id_1), None)
        exp2 = next((e for e in self.experiments if e.config.experiment_id == exp_id_2), None)
        if not exp1 or not exp2:
            return None

        return {
            "experiment_1": exp1.config.name,
            "experiment_2": exp2.config.name,
            "comparisons": [
                {
                    "metric": s1.metric_name,
                    "exp1_mean": s1.mean_a,
                    "exp2_mean": s2.mean_a,
                    "delta": round(s1.mean_a - s2.mean_a, 2),
                    "delta_pct": round((s1.mean_a - s2.mean_a) / max(0.01, abs(s2.mean_a)) * 100, 1)
                }
                for s1, s2 in zip(exp1.statistical_results, exp2.statistical_results)
                if s1.metric_name == s2.metric_name
            ]
        }

    def _save_result(self, result: ExperimentResult):
        path = self.output_dir / f"{result.config.experiment_id}.json"
        data = {
            "experiment_id": result.config.experiment_id,
            "name": result.config.name,
            "hypothesis": result.config.hypothesis,
            "started_at": result.started_at,
            "completed_at": result.completed_at,
            "summary": result.summary,
            "statistics": [
                {
                    "metric": s.metric_name,
                    "mean_a": s.mean_a, "mean_b": s.mean_b,
                    "p_value": s.p_value, "cohens_d": s.cohens_d,
                    "significant": s.significant,
                    "effect_size": s.effect_size_label
                }
                for s in result.statistical_results
            ],
            "errors": result.errors
        }
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def load_result(self, experiment_id: str) -> Optional[dict]:
        path = self.output_dir / f"{experiment_id}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return None

    def generate_report(self, experiment_id: str) -> str:
        result = next((e for e in self.experiments if e.config.experiment_id == experiment_id), None)
        if not result:
            data = self.load_result(experiment_id)
            if not data:
                return f"Experimento {experiment_id} nao encontrado"
            return self._format_report_from_dict(data)

        lines = [
            f"# Relatorio de Experimento: {result.config.name}",
            f"**ID:** {result.config.experiment_id}",
            f"**Hipotese:** {result.config.hypothesis}",
            f"**Repeticoes:** {result.config.repetitions}",
            f"**Periodo:** {result.started_at} -> {result.completed_at}",
            "",
            f"| Metrica | Media A | Media B | p-valor | Cohen's d | Efeito | Signif. |",
            f"|---------|---------|---------|---------|-----------|--------|---------|",
        ]

        for s in result.statistical_results:
            sig = "SIM" if s.significant else "nao"
            lines.append(
                f"| {s.metric_name} | {s.mean_a:.2f} | {s.mean_b:.2f} | "
                f"{s.p_value:.4f} | {s.cohens_d:.3f} | {s.effect_size_label} | {sig} |"
            )

        lines.extend([
            "",
            f"**Resumo:** {result.summary}",
            f"**Conclusao:** {'Hipotese confirmada' if any(s.significant for s in result.statistical_results) else 'Sem evidencia suficiente'}",
        ])

        return "\n".join(lines)

    @staticmethod
    def _format_report_from_dict(data: dict) -> str:
        lines = [
            f"# Relatorio de Experimento: {data.get('name', 'N/A')}",
            f"**ID:** {data.get('experiment_id', 'N/A')}",
            f"**Hipotese:** {data.get('hypothesis', 'N/A')}",
            "",
            f"| Metrica | Media A | Media B | p-valor | Cohen's d | Signif. |",
            f"|---------|---------|---------|---------|-----------|---------|",
        ]
        for s in data.get("statistics", []):
            sig = "SIM" if s.get("significant") else "nao"
            lines.append(
                f"| {s['metric']} | {s['mean_a']:.2f} | {s['mean_b']:.2f} | "
                f"{s['p_value']:.4f} | {s['cohens_d']:.3f} | {sig} |"
            )
        return "\n".join(lines)
