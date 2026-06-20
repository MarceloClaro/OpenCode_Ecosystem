#!/bin/bash
cd /mnt/c/Users/marce/Documents/OpenCode_Ecosystem

git add AUDIT_REPORT_N35.md
git add README.md
git add .opencode/
git add .impact/
git add .tdd-sdd/

git commit -m "docs(audit): relatorio de autopoiese N3.5+ e atualizacao do README"
git push origin main || git push origin master
