#!/bin/bash
git config core.fileMode false
git add .opencode/engines/orchestration_engine.js
git add .opencode/run_n4_singularity.js
git add .tdd-sdd/SPECIFICATIONS.md
git add .tdd-sdd/tests/test_n4_liquid_swarm.js
git add .tdd-sdd/tests/test_n35_evolution.js
git add .impact/reports/audit_n35_evolution.txt
git commit -m "feat(arch): transcend to N4.0 Liquid Swarm Architecture"
git push origin main
