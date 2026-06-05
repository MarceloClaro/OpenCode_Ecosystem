#!/usr/bin/env python3
"""
Example helper script for reasoning-orchestrator

Demonstrates how to parse and validate a Checkpoint Nexus configuration.
"""

def validate_checkpoint(checkpoint: dict) -> list[str]:
    errors = []
    if "depth" not in checkpoint:
        errors.append("Missing 'depth' (L1-L4)")
    if "reasoning_types" not in checkpoint:
        errors.append("Missing 'reasoning_types'")
    if "domain" not in checkpoint:
        errors.append("Missing 'domain'")
    if "barrier" not in checkpoint:
        errors.append("Missing 'barrier' (falsificationist, bias, or none)")
    return errors

def main():
    example = {
        "depth": "L3",
        "reasoning_types": ["bayesian", "systemic"],
        "domain": "IA & LLMs",
        "barrier": "falsificationist"
    }
    errors = validate_checkpoint(example)
    if errors:
        print(f"Validation errors: {errors}")
    else:
        print("Checkpoint Nexus validado com sucesso!")

if __name__ == "__main__":
    main()
