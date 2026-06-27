#!/usr/bin/env python3
"""
APA Academic Writing Validator
Valida conformidade de documentos acadêmicos com normas APA 7ª edição
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class APAValidator:
    """Validador de normas APA 7ª edição"""
    
    def __init__(self):
        # Padrões de citação APA
        self.citation_patterns = {
            'narrative': r'[A-Z][a-záàãâéêíóôõúüç]+(?:\s(?:&|e|et\sal\.)\s[A-Z][a-záàãâéêíóôõúüç]+)*\s\(\d{4}[a-z]?\)',
            'parenthetical': r'\([A-Z][a-záàãâéêíóôõúüç]+(?:\s(?:&|e|et\sal\.)\s[A-Z][a-záàãâéêíóôõúüç]+)*,\s\d{4}[a-z]?\)',
        }
        
        # Padrão de referência APA
        self.reference_pattern = r'^[A-Z][a-záàãâéêíóôõúüç]+,\s[A-Z]\.\s(?:[A-Z]\.\s)?\(\d{4}[a-z]?\)\.\s.+'
        
        # Estrutura obrigatória do PF
        self.pf_structure = [
            'Introdução',
            'Marco Teórico',
            'Metodologia',
            'Resultados',
            'Discussão',
            'Conclusões',
            'Referências'
        ]
        
        # Configurações de página APA
        self.page_config = {
            'margins_cm': 2.54,
            'line_spacing': 'double',
            'font': 'Times New Roman',
            'font_size': 12,
            'alignment': 'justified',
            'paragraph_indent_cm': 1.27
        }
    
    def validate_file(self, file_path: str) -> Dict:
        """Valida um arquivo completo"""
        results = {
            'file': file_path,
            'issues': [],
            'warnings': [],
            'score': 0,
            'details': {}
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            results['issues'].append(f"Erro ao ler arquivo: {str(e)}")
            return results
        
        # Validações
        results['details']['structure'] = self.validate_structure(content)
        results['details']['citations'] = self.validate_citations(content)
        results['details']['references'] = self.validate_references(content)
        results['details']['formatting'] = self.validate_formatting(content)
        
        # Calcula pontuação
        total_checks = 0
        passed_checks = 0
        
        for detail in results['details'].values():
            if isinstance(detail, dict):
                total_checks += detail.get('total', 0)
                passed_checks += detail.get('passed', 0)
        
        results['score'] = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Coleta issues e warnings
        for detail in results['details'].values():
            if isinstance(detail, dict):
                results['issues'].extend(detail.get('issues', []))
                results['warnings'].extend(detail.get('warnings', []))
        
        return results
    
    def validate_structure(self, content: str) -> Dict:
        """Valida estrutura do documento"""
        result = {'total': 0, 'passed': 0, 'issues': [], 'warnings': []}
        
        # Verifica seções obrigatórias
        for section in self.pf_structure:
            result['total'] += 1
            if re.search(rf'#+\s*{section}', content, re.IGNORECASE):
                result['passed'] += 1
            else:
                result['issues'].append(f"Seção '{section}' não encontrada")
        
        # Verifica se tem resumo/abstract
        result['total'] += 1
        if re.search(r'#+\s*(Resumo|Abstract)', content, re.IGNORECASE):
            result['passed'] += 1
        else:
            result['warnings'].append("Seção 'Resumo/Abstract' não encontrada")
        
        return result
    
    def validate_citations(self, content: str) -> Dict:
        """Valida citações no texto"""
        result = {'total': 0, 'passed': 0, 'issues': [], 'warnings': []}
        
        # Procura por citações
        citations_found = []
        
        # Citações narrativas
        narrative = re.findall(self.citation_patterns['narrative'], content)
        citations_found.extend(narrative)
        
        # Citações parentéticas
        parenthetical = re.findall(self.citation_patterns['parenthetical'], content)
        citations_found.extend(parenthetical)
        
        result['total'] = len(citations_found)
        result['passed'] = len(citations_found)  # Simplificado
        
        # Verifica citações numéricas (não-APA)
        numeric_citations = re.findall(r'\[\d+\]', content)
        if numeric_citations:
            result['issues'].append(f"Encontradas {len(numeric_citations)} citações numéricas (não-APA)")
        
        # Verifica se há referências correspondentes
        if citations_found:
            result['warnings'].append(f"Encontradas {len(citations_found)} citações - verificar correspondência com Referências")
        
        return result
    
    def validate_references(self, content: str) -> Dict:
        """Valida seção de referências"""
        result = {'total': 0, 'passed': 0, 'issues': [], 'warnings': []}
        
        # Procura por seção de referências
        ref_section = re.search(r'#+\s*(Referências|References|Bibliografia)\s*\n(.*?)(?=\n#|\Z)', content, re.DOTALL | re.IGNORECASE)
        
        if not ref_section:
            result['issues'].append("Seção de Referências não encontrada")
            return result
        
        ref_content = ref_section.group(2)
        references = [line.strip() for line in ref_content.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        result['total'] = len(references)
        
        # Valida cada referência
        for ref in references:
            if re.match(self.reference_pattern, ref):
                result['passed'] += 1
            else:
                result['issues'].append(f"Referência fora do formato APA: {ref[:50]}...")
        
        # Verifica ordenação alfabética
        if references:
            sorted_refs = sorted(references, key=lambda x: x.split(',')[0].lower())
            if references != sorted_refs:
                result['warnings'].append("Referências não estão em ordem alfabética")
        
        return result
    
    def validate_formatting(self, content: str) -> Dict:
        """Valida formatação básica"""
        result = {'total': 0, 'passed': 0, 'issues': [], 'warnings': []}
        
        # Verifica se tem numeração de páginas (indica formatação)
        result['total'] += 1
        if re.search(r'\d+', content):
            result['passed'] += 1
        
        # Verifica se tem títulos formatados
        result['total'] += 1
        if re.search(r'#+\s', content):
            result['passed'] += 1
        
        # Verifica se tem listas (pode indicar formatação)
        result['total'] += 1
        if re.search(r'^\s*[-*]\s', content, re.MULTILINE):
            result['passed'] += 1
        
        # Verifica comprimento de linhas (APA recomenda < 65 caracteres)
        lines = content.split('\n')
        long_lines = [i for i, line in enumerate(lines) if len(line) > 80]
        if long_lines:
            result['warnings'].append(f"Encontradas {len(long_lines)} linhas com mais de 80 caracteres")
        
        return result
    
    def generate_report(self, results: Dict) -> str:
        """Gera relatório de validação"""
        report = []
        report.append("=" * 60)
        report.append("RELATÓRIO DE VALIDAÇÃO APA 7ª EDIÇÃO")
        report.append("=" * 60)
        report.append(f"Arquivo: {results['file']}")
        report.append(f"Pontuação: {results['score']:.1f}%")
        report.append("")
        
        # Issues críticos
        if results['issues']:
            report.append("❌ PROBLEMAS ENCONTRADOS:")
            for issue in results['issues']:
                report.append(f"  • {issue}")
            report.append("")
        
        # Warnings
        if results['warnings']:
            report.append("⚠️  ALERTAS:")
            for warning in results['warnings']:
                report.append(f"  • {warning}")
            report.append("")
        
        # Detalhes por categoria
        report.append("📊 DETALHES POR CATEGORIA:")
        for category, details in results['details'].items():
            if isinstance(details, dict) and 'total' in details:
                total = details['total']
                passed = details['passed']
                percentage = (passed / total * 100) if total > 0 else 0
                report.append(f"  {category.upper()}: {passed}/{total} ({percentage:.0f}%)")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python apa_validator.py <arquivo>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"Erro: Arquivo '{file_path}' não encontrado")
        sys.exit(1)
    
    validator = APAValidator()
    results = validator.validate_file(file_path)
    report = validator.generate_report(results)
    
    print(report)
    
    # Retorna código de saída baseado na pontuação
    sys.exit(0 if results['score'] >= 80 else 1)


if __name__ == "__main__":
    main()