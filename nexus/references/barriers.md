<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Nexus-Multiagents-v6 (NMA) - Detailed Sync Barriers

This reference contains the full list of 120+ Synchronization Barriers (SB) and their specific constraints.

## Layer 0: Meta-Coordination (5 Barriers)
- **SB0.1: Context Alignment** (Is the task suitable for NMA?)
- **SB0.2: Resource Pre-Allocation** (Check MCP availability)
- **SB0.3: Meta-Strategy Selection** (Which reasoning sub-types to prioritize?)
- **SB0.4: Goal Decomposition** (Break into atomic operations)
- **SB0.5: Execution Monitoring** (Watch the watchers)

## Layer 1: Domain Discovery (15 Barriers)
- **SB1.1-1.4: Concept Extraction** (70 constraints)
- **SB1.5-1.8: Relation Discovery** (60 constraints)
- **SB1.9-1.12: Law Inference** (50 constraints)
- **SB1.13-1.15: Problem Classification** (40 constraints)

## Layer 2: Autonomous Reasoning (20 Barriers)
- **SB2.1-2.4: Analyze Characteristics** (80 constraints)
- **SB2.5-2.8: Select Reasoning Type** (90 constraints)
- **SB2.9-2.12: Configure Parameters** (70 constraints)
- **SB2.13-2.17: Validate Strategy** (100 constraints)
- **SB2.18-2.20: Self-Reflection** (60 constraints)

## Layer 3: MCP Organization (25 Barriers)
- **SB3.1-3.5: Discover MCPs** (80 constraints)
- **SB3.6-3.9: Analyze Requirements** (70 constraints)
- **SB3.10-3.14: Match MCPs** (90 constraints)
- **SB3.15-3.19: Negotiate Contracts** (80 constraints)
- **SB3.20-3.24: Form Team** (100 constraints)
- **SB3.25: Plan Fallback** (40 constraints)

## Layer 4: Specialization (30 Barriers)
- **SB4.1-4.10: Analyze Success Patterns** (150 constraints)
- **SB4.11-4.20: Adapt Capabilities** (140 constraints)
- **SB4.21-4.30: Specialize Agents** (130 constraints)

## Layer 5: Self-Healing (30 Barriers)
- **SB5.1-5.10: Monitor Health** (120 constraints)
- **SB5.11-5.20: Detect Failures** (110 constraints)
- **SB5.21-5.30: Recover Automatically** (130 constraints)
- **SB5.31-5.40: Prevent Future Failures** (100 constraints)

---

### Constraint Types
- **NUMERIC_RANGE**: Min/max values
- **NUMERIC_COMPARISON**: Comparisons (>, <, ==)
- **STRING_PATTERN**: Regex patterns
- **COLLECTION_SIZE**: Collection size
- **EXISTENCE**: Existence check
- **TYPE_CHECK**: Type validation
- **CUSTOM**: Domain-specific logic
