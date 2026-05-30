# -*- coding: utf-8 -*-
# SAÃDA OBRIGATÃ“RIA: PORTUGUÃŠS BRASILEIRO FORMAL
# Toda resposta ao usuÃ¡rio DEVE ser em portuguÃªs do Brasil formal.
# Contexto em chinÃªs para eficiÃªncia de tokens (densidade +40%%).
# Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)

#!/usr/bin/env python3
"""
Evolution Optimizer: Continuous fitness scoring and mutation analysis.

Manages:
- Fitness score calculation (multi-criteria)
- Mutation proposals and validation
- Lineage tracking and genetic history
- Adaptive barrier adjustment
- Rollback recommendations
"""

import json
import os
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib


@dataclass
class FitnessMetrics:
    """Metrics for fitness calculation."""
    success_rate: float  # 0.0 to 1.0
    speed_factor: float  # baseline_time / actual_time
    quality_score: float  # 0.0 to 1.0
    resource_efficiency: float  # 0.0 to 1.0
    innovation_factor: float  # 0.0 to 1.0
    
    def calculate_fitness(self) -> float:
        """Calculate weighted fitness score."""
        fitness = (
            0.30 * self.success_rate +
            0.25 * self.speed_factor +
            0.20 * self.quality_score +
            0.15 * self.resource_efficiency +
            0.10 * self.innovation_factor
        )
        return max(0.0, min(1.0, fitness))


class EvolutionOptimizer:
    """Manages system evolution and optimization."""
    
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
        self.state_file = os.path.join(skill_path, "system_state.json")
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load or initialize system state."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            "evolution_version": "2.0.0",
            "fitness_history": [],
            "mutation_history": [],
            "active_mutations": {},
            "lineage": {},
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _save_state(self) -> None:
        """Save system state to file."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def calculate_fitness(self, metrics: Dict[str, float]) -> float:
        """Calculate fitness score from metrics."""
        fm = FitnessMetrics(
            success_rate=metrics.get("success_rate", 0.5),
            speed_factor=metrics.get("speed_factor", 1.0),
            quality_score=metrics.get("quality_score", 0.5),
            resource_efficiency=metrics.get("resource_efficiency", 0.8),
            innovation_factor=metrics.get("innovation_factor", 0.5)
        )
        return fm.calculate_fitness()
    
    def evaluate_cycle(self, cycle_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a development cycle."""
        fitness = self.calculate_fitness(cycle_metrics)
        
        # Record fitness history
        self.state["fitness_history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fitness_score": fitness,
            "metrics": cycle_metrics
        })
        
        # Determine if mutations are needed
        mutations_needed = []
        
        if fitness < 0.7:
            mutations_needed.append({
                "type": "rigor_increase",
                "target": "SB1",
                "reason": "Low fitness score detected",
                "severity": "high"
            })
        
        if cycle_metrics.get("quality_score", 0) < 0.6:
            mutations_needed.append({
                "type": "review_required",
                "target": "A4",
                "reason": "Quality score below threshold",
                "severity": "medium"
            })
        
        if cycle_metrics.get("success_rate", 0) < 0.8:
            mutations_needed.append({
                "type": "barrier_adjustment",
                "target": "Sync Barriers",
                "reason": "Success rate below baseline",
                "severity": "medium"
            })
        
        # Check for rollback necessity
        rollback_needed = False
        if len(self.state["fitness_history"]) > 1:
            current_fitness = fitness
            previous_fitness = self.state["fitness_history"][-2]["fitness_score"]
            
            # Rollback if fitness drops >20%
            if (previous_fitness - current_fitness) / previous_fitness > 0.2:
                rollback_needed = True
        
        return {
            "fitness_score": fitness,
            "mutations_needed": mutations_needed,
            "rollback_needed": rollback_needed,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def propose_mutation(
        self,
        mutation_type: str,
        target: str,
        reason: str,
        severity: str = "medium"
    ) -> Dict[str, Any]:
        """Propose a mutation to the system."""
        mutation = {
            "id": f"mut-{datetime.now(timezone.utc).timestamp()}",
            "type": mutation_type,
            "target": target,
            "reason": reason,
            "severity": severity,
            "proposed_at": datetime.now(timezone.utc).isoformat(),
            "status": "proposed"
        }
        
        self.state["mutation_history"].append(mutation)
        return mutation
    
    def validate_mutation(self, mutation_id: str, approved: bool) -> Dict[str, Any]:
        """Validate a proposed mutation."""
        mutation = next(
            (m for m in self.state["mutation_history"] if m["id"] == mutation_id),
            None
        )
        
        if not mutation:
            raise ValueError(f"Mutation {mutation_id} not found")
        
        mutation["status"] = "approved" if approved else "rejected"
        mutation["validated_at"] = datetime.now(timezone.utc).isoformat()
        
        if approved:
            self.state["active_mutations"][mutation["target"]] = mutation
        
        return mutation
    
    def get_agent_lineage(self, agent_id: str) -> Dict[str, Any]:
        """Get lineage information for an agent."""
        if agent_id not in self.state["lineage"]:
            self.state["lineage"][agent_id] = {
                "agent_id": agent_id,
                "generation": 1,
                "parent_ids": [],
                "transformations": [],
                "fitness_scores": []
            }
        
        return self.state["lineage"][agent_id]
    
    def record_transformation(
        self,
        agent_id: str,
        transformation_type: str,
        fitness_delta: float
    ) -> None:
        """Record an agent transformation."""
        lineage = self.get_agent_lineage(agent_id)
        
        lineage["transformations"].append({
            "type": transformation_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fitness_delta": fitness_delta
        })
        
        lineage["generation"] += 1
    
    def check_guardrails(self, agent_id: str) -> Dict[str, Any]:
        """Check evolution guardrails for an agent."""
        lineage = self.get_agent_lineage(agent_id)
        
        guardrails = {
            "mutation_limit_exceeded": len(lineage["transformations"]) > 3,
            "fitness_floor_violated": any(
                score < 0.4 for score in lineage["fitness_scores"]
            ),
            "generation_limit_exceeded": lineage["generation"] > 20,
            "status": "ok"
        }
        
        if any(guardrails.values()):
            guardrails["status"] = "violation_detected"
        
        return guardrails
    
    def export_evolution_report(self, filepath: str) -> None:
        """Export evolution report to JSON."""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fitness_history": self.state["fitness_history"][-100:],  # Last 100
            "mutation_history": self.state["mutation_history"][-50:],  # Last 50
            "active_mutations": self.state["active_mutations"],
            "lineage_summary": {
                agent_id: {
                    "generation": lineage["generation"],
                    "transformations": len(lineage["transformations"]),
                    "avg_fitness": (
                        sum(lineage["fitness_scores"]) / len(lineage["fitness_scores"])
                        if lineage["fitness_scores"] else 0.0
                    )
                }
                for agent_id, lineage in self.state["lineage"].items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
    
    def update_system_state(self, new_metrics: Dict[str, Any]) -> float:
        """Update system state with new metrics (legacy interface)."""
        fitness = self.calculate_fitness(new_metrics)
        self.state["fitness_score"] = fitness
        self.state["fitness_history"].append(fitness)
        
        # Legacy mutation logic
        if fitness < 0.7:
            self.state["active_mutations"] = {
                "SB1_rigor": "High",
                "A4_review_required": True
            }
        else:
            self.state["active_mutations"] = {
                "SB1_rigor": "Normal",
                "A4_review_required": False
            }
        
        self._save_state()
        return fitness


def main():
    """Command-line interface."""
    if len(sys.argv) < 3:
        print("Usage: python evolution_optimizer.py <skill_dir> <metrics_json_str>")
        print("       python evolution_optimizer.py <skill_dir> --export <output_file>")
        sys.exit(1)
    
    skill_dir = sys.argv[1]
    optimizer = EvolutionOptimizer(skill_dir)
    
    if sys.argv[2] == "--export" and len(sys.argv) > 3:
        output_file = sys.argv[3]
        optimizer.export_evolution_report(output_file)
        print(f"Evolution report exported to {output_file}")
    else:
        try:
            metrics = json.loads(sys.argv[2])
            score = optimizer.update_system_state(metrics)
            print(f"Evolution Update: New Fitness Score = {score:.2f}")
        except json.JSONDecodeError as e:
            print(f"Error parsing metrics JSON: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
