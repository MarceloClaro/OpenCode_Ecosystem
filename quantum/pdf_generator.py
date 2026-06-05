"""
Gerador de Relatórios PDF para Análise QML
Cria PDFs com análise completa, Grad-CAM e referências científicas
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import io
import base64
from typing import Dict, List, Optional

class QMLReportGenerator:
    """Gerador de relatórios PDF para análise QML"""
    
    def __init__(self, filename: str = None):
        """
        Inicializar gerador
        
        Args:
            filename: Caminho do arquivo PDF (se None, retorna bytes)
        """
        self.filename = filename or "qml_report.pdf"
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos customizados"""
        self.styles.add(ParagraphStyle(
            name='Title',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00d9ff'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading2Custom',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#00d9ff'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyCustom',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
    
    def add_title(self, title: str, subtitle: str = None):
        """Adicionar título ao relatório"""
        self.story.append(Paragraph(title, self.styles['Title']))
        
        if subtitle:
            self.story.append(Paragraph(
                f"<i>{subtitle}</i>",
                ParagraphStyle(
                    'Subtitle',
                    parent=self.styles['Normal'],
                    fontSize=12,
                    textColor=colors.HexColor('#9d4edd'),
                    alignment=TA_CENTER,
                    spaceAfter=20
                )
            ))
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_metadata(self, metadata: Dict):
        """Adicionar metadados do relatório"""
        data = [
            ['Campo', 'Valor'],
            ['Data de Geração', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
            ['Arquivo Analisado', metadata.get('imageName', 'N/A')],
            ['Versão do Modelo', metadata.get('modelVersion', '1.0')],
            ['Dispositivo', metadata.get('device', 'Simulador')],
        ]
        
        table = Table(data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00d9ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#334155')),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_classification_results(self, results: Dict):
        """Adicionar resultados de classificação"""
        self.story.append(Paragraph("Resultados da Classificação", self.styles['Heading2Custom']))
        
        # Tabela de resultados
        data = [
            ['Métrica', 'Valor'],
            ['Classe Predita', results.get('predicted_class', 'N/A')],
            ['Confiança', f"{results.get('confidence', 0):.2f}%"],
            ['Tempo de Inferência', f"{results.get('inference_time', 0):.3f}s"],
            ['Versão do Modelo', results.get('model_version', '1.0')],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9d4edd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4a5568')),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_probabilities(self, probabilities: List[Dict]):
        """Adicionar distribuição de probabilidades"""
        self.story.append(Paragraph("Distribuição de Probabilidades por Classe", self.styles['Heading2Custom']))
        
        data = [['Classe', 'Probabilidade']]
        for prob in probabilities:
            data.append([
                prob.get('class', 'N/A'),
                f"{prob.get('probability', 0):.2f}%"
            ])
        
        table = Table(data, colWidths=[2.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00d9ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4a5568')),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_gradcam_image(self, gradcam_base64: str, caption: str = "Visualização Grad-CAM"):
        """Adicionar imagem Grad-CAM"""
        self.story.append(Paragraph("Interpretabilidade - Grad-CAM", self.styles['Heading2Custom']))
        
        try:
            # Decodificar base64
            if "," in gradcam_base64:
                gradcam_base64 = gradcam_base64.split(",")[1]
            
            image_data = base64.b64decode(gradcam_base64)
            image_file = io.BytesIO(image_data)
            
            # Adicionar imagem
            img = Image(image_file, width=4*inch, height=4*inch)
            self.story.append(img)
            
            self.story.append(Spacer(1, 0.1*inch))
            self.story.append(Paragraph(
                f"<i>{caption}</i>",
                ParagraphStyle(
                    'Caption',
                    parent=self.styles['Normal'],
                    fontSize=9,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor('#9d4edd')
                )
            ))
        except Exception as e:
            self.story.append(Paragraph(
                f"<b>Erro ao carregar Grad-CAM:</b> {str(e)}",
                self.styles['Normal']
            ))
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_mitigation_stats(self, stats: Dict):
        """Adicionar estatísticas de mitigação de erros"""
        self.story.append(Paragraph("Mitigação de Erros Quânticos", self.styles['Heading2Custom']))
        
        data = [
            ['Técnica', 'Resultado'],
            ['ZNE (Zero Noise Extrapolation)', f"{stats.get('zne_result', 0):.4f}"],
            ['PEC (Probabilistic Error Cancellation)', f"{stats.get('pec_result', 0):.4f}"],
            ['Resultado Híbrido', f"{stats.get('hybrid_result', 0):.4f}"],
            ['Peso ZNE', f"{stats.get('zne_weight', 0):.1%}"],
            ['Peso PEC', f"{stats.get('pec_weight', 0):.1%}"],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4a5568')),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_references(self, references: List[Dict]):
        """Adicionar referências científicas"""
        self.story.append(Paragraph("Referências Científicas", self.styles['Heading2Custom']))
        
        for i, ref in enumerate(references[:10], 1):  # Limitar a 10 referências
            ref_text = f"""
            <b>[{i}]</b> {ref.get('authors', 'N/A')} ({ref.get('year', 'N/A')}). 
            <i>{ref.get('title', 'N/A')}</i>. 
            {ref.get('journal', 'N/A')}. 
            DOI: {ref.get('doi', 'N/A')}
            """
            self.story.append(Paragraph(ref_text, self.styles['BodyCustom']))
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_methodology(self):
        """Adicionar seção de metodologia"""
        self.story.append(Paragraph("Metodologia", self.styles['Heading2Custom']))
        
        methodology_text = """
        <b>Arquitetura do Modelo:</b> Variational Quantum Classifier (VQC) com 50 qubits, 
        6 camadas de ansatz hardware-efficient, e mitigação híbrida de erros (ZNE+PEC).
        <br/><br/>
        <b>Codificação:</b> Amplitude encoding com normalização de features.
        <br/><br/>
        <b>Mitigação de Erros:</b> Zero Noise Extrapolation (ZNE) com extrapolação linear 
        e Probabilistic Error Cancellation (PEC) com 100 amostras.
        <br/><br/>
        <b>Dataset:</b> HAM10000 com 10.015 imagens de lesões de pele em 7 classes diagnósticas.
        <br/><br/>
        <b>Validação:</b> 5-Fold Cross-Validation com estratificação, Bootstrap 1000 iterações 
        para intervalo de confiança 95%, e testes estatísticos (McNemar, Cochran Q, Binomial).
        """
        
        self.story.append(Paragraph(methodology_text, self.styles['BodyCustom']))
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_conclusions(self, conclusions: str):
        """Adicionar conclusões"""
        self.story.append(Paragraph("Conclusões", self.styles['Heading2Custom']))
        self.story.append(Paragraph(conclusions, self.styles['BodyCustom']))
        self.story.append(Spacer(1, 0.3*inch))
    
    def generate(self) -> bytes:
        """
        Gerar PDF
        
        Returns:
            Bytes do PDF gerado
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        doc.build(self.story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def save(self, filepath: str):
        """
        Salvar PDF em arquivo
        
        Args:
            filepath: Caminho do arquivo
        """
        pdf_bytes = self.generate()
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)


def generate_analysis_report(analysis_data: Dict) -> bytes:
    """
    Gerar relatório PDF completo de análise
    
    Args:
        analysis_data: Dicionário com dados de análise
        
    Returns:
        Bytes do PDF
    """
    generator = QMLReportGenerator()
    
    # Título
    generator.add_title(
        "Relatório de Análise QML",
        "Classificação de Imagens Médicas com Máquina Quântica Variacional"
    )
    
    # Metadados
    generator.add_metadata(analysis_data)
    
    # Resultados
    generator.add_classification_results(analysis_data)
    
    # Probabilidades
    if 'probabilities' in analysis_data:
        generator.add_probabilities(analysis_data['probabilities'])
    
    # Grad-CAM
    if 'gradcam' in analysis_data:
        generator.add_gradcam_image(analysis_data['gradcam'])
    
    # Mitigação
    if 'mitigation_stats' in analysis_data:
        generator.add_mitigation_stats(analysis_data['mitigation_stats'])
    
    # Metodologia
    generator.add_methodology()
    
    # Conclusões
    conclusions = f"""
    A análise foi realizada com sucesso usando um Variational Quantum Classifier 
    com mitigação híbrida de erros. A classe predita é <b>{analysis_data.get('predicted_class', 'N/A')}</b> 
    com confiança de <b>{analysis_data.get('confidence', 0):.2f}%</b>. 
    As técnicas de mitigação ZNE e PEC foram aplicadas para melhorar a robustez 
    da predição contra erros quânticos.
    """
    generator.add_conclusions(conclusions)
    
    # Referências
    references = [
        {
            "authors": "Cerezo, M., et al.",
            "year": 2021,
            "title": "Variational quantum algorithms",
            "journal": "Nature Reviews Physics",
            "doi": "10.1038/s42254-021-00348-7"
        },
        {
            "authors": "Kandala, A., et al.",
            "year": 2017,
            "title": "Hardware-efficient variational quantum eigensolver",
            "journal": "Nature",
            "doi": "10.1038/nature23879"
        },
        {
            "authors": "Temme, K., et al.",
            "year": 2017,
            "title": "Error mitigation for quantum computing",
            "journal": "Physical Review Letters",
            "doi": "10.1103/PhysRevLett.119.180509"
        },
    ]
    generator.add_references(references)
    
    return generator.generate()


if __name__ == "__main__":
    print("PDF Generator Module Initialized")
