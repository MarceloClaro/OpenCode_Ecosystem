#!/usr/bin/env python3
"""
WhatsApp Cognitive Profiler — Extrai perfis cognitivos de chats reais.
Converte mensagens de grupos WhatsApp em SimAgent profiles calibrados
para validação externa da simulação MiroFish.

Compatível com: whatsapp-mcp (github.com/MarceloClaro/whatsapp-mcp)
Formato de entrada: export do WhatsApp (.txt) ou JSON do MCP.
"""

import re, json, os, math
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional, Tuple

BRAZIL_TZ = timezone(timedelta(hours=-3))

# ── Padrões de parse de chat WhatsApp ──
# Formato brasileiro: "DD/MM/YYYY HH:MM - Nome: mensagem"
# Formato internacional: "MM/DD/YY, HH:MM - Name: message"
# Formato sistema: "[DD/MM/YYYY HH:MM:SS] Nome: mensagem"

RE_BR = re.compile(r'^(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})\s*[-–]\s*([^:]+?):\s*(.+)$')
RE_INTL = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[APap][Mm])?)\s*[-–]\s*([^:]+?):\s*(.+)$')
RE_SYSTEM = re.compile(r'^\[(\d{2}/\d{2}/\d{4}),?\s+(\d{2}:\d{2}(?::\d{2})?)\]\s*([^:]+?):\s*(.+)$')
RE_MEDIA = re.compile(r'(<Mídia oculta>|<Media omitted>|image omitted|video omitted|sticker omitted|audio omitted|GIF omitted)', re.I)
RE_SYSTEM_MSG = re.compile(r'(criou o grupo|adicionou|removeu|saiu|alterou|mudou|entrou|Mensagens.*são protegidas)', re.I)

# ── Dicionários de análise textual ──
STANCE_KEYWORDS = {
    "supportive": [
        "concordo", "excelente", "ótimo", "perfeito", "apoio", "apoiar",
        " parabéns", "top", "show", "boa", "bom trabalho", "sensacional",
        "verdade", "isso mesmo", "exatamente", "sim ", "claro que",
        "com certeza", "faz sentido", "gostei", "muito bom",
    ],
    "critical": [
        "discordo", "não concordo", "errado", "absurdo", "inaceitável",
        "problema", "péssimo", "horrível", "não funciona", "incompetente",
        "mentira", "fake", "engano", "não é verdade", "discutível",
        "questionável", "preocupante", "grave", "crítico",
    ],
    "curious": [
        "como funciona", "por que", "qual a fonte", "me explica",
        "não entendi", "pode elaborar", "interessante", "curioso",
        "como assim", "detalhe", "esclarecer", "dúvida", "pergunta",
        "explica melhor", "fonte?", "link?", "onde viu",
    ],
    "neutral": [
        "ok", "obrigado", "valeu", "blz", "👍", "👏", "😂", "🤣",
        "bom dia", "boa tarde", "boa noite", "tmj", "abraço",
    ],
}

TOPIC_KEYWORDS = {
    # Economia (15)
    "economia": ["economia", "pib", "inflação", "dólar", "real", "juros", "selic", "mercado", "investimento", "fiscal", "dívida", "orçamento", "consumo", "produção", "crescimento", "recessão", "recuperação", "ciclo", "conjuntura"],
    "inflacao": ["inflação", "ipca", "igpm", "preço", "carestia", "custo de vida", "inflacionário", "hiperinflação", "indexação"],
    "desemprego": ["desemprego", "desempregado", "vaga", "contratação", "demissão", "layoff", "subemprego", "informalidade", "caged", "poupança"],
    "crescimento_pib": ["pib", "produto interno", "crescimento", "expansão", "contração", "atividade econômica", "trimestre"],
    "juros_selic": ["selic", "juros", "copom", "banco central", "taxa básica", "política monetária", "aperto monetário", "afrouxamento"],
    "cambio_dolar": ["dólar", "câmbio", "real", "cambio", "moeda", "desvalorização", "valorização", "forex", "ptax"],
    "divida_publica": ["dívida pública", "déficit", "superávit", "primário", "resultado fiscal", "teto de gastos", "arcabouço", "responsabilidade fiscal"],
    "reforma_tributaria": ["reforma tributária", "imposto", "iva", "cbs", "ibs", "simplificação", "tributação", "taxação", "sonegação"],
    "balanca_comercial": ["balança comercial", "exportação", "importação", "superávit comercial", "déficit comercial", "commodities"],
    "investimento_estrangeiro": ["investimento estrangeiro", "ied", "capital externo", "multinacional", "desinvestimento", "fuga de capital"],
    "credito": ["crédito", "empréstimo", "financiamento", "endividamento", "inadimplência", "serasa", "spc", "juros altos", "consignado"],
    "industria_nacional": ["indústria", "industrial", "manufatura", "produção industrial", "neoindustrialização", "desindustrialização"],
    "agronegocio": ["agronegócio", "agro", "agricultura", "pecuária", "soja", "milho", "café", "carne", "exportação agrícola", "safra"],
    "comercio_exterior": ["comércio exterior", "exportações", "importações", "barreiras", "tarifas", "protecionismo", "acordos comerciais", "omc"],
    "mercado_trabalho": ["mercado de trabalho", "clt", "pj", "pejotização", "terceirização", "sindicato", "direitos trabalhistas", "salário mínimo", "dissídio"],

    # Social (15)
    "desigualdade": ["desigualdade", "pobreza", "rico", "pobre", "gini", "bolsa família", "renda", "salário mínimo", "favela", "elite", "privilégio", "distribuição", "concentração de renda", "ascensão social"],
    "pobreza": ["pobreza", "miséria", "fome", "vulnerabilidade", "assistência", "transferência de renda", "auxílio", "cadunico", "miserável"],
    "fome": ["fome", "insegurança alimentar", "desnutrição", "subnutrição", "merenda escolar", "alimentação", "cesta básica"],
    "moradia": ["moradia", "habitação", "casa própria", "aluguel", "sem teto", "cortiço", "ocupação", "minha casa minha vida", "déficit habitacional"],
    "saneamento": ["saneamento", "esgoto", "água potável", "tratamento", "sabesp", "privatização", "marco do saneamento"],
    "transporte_publico": ["transporte público", "ônibus", "metrô", "mobilidade", "tarifa", "passe livre", "bilhete único", "lotação"],
    "seguranca_publica": ["segurança pública", "polícia", "crime", "homicídio", "assalto", "roubo", "latrocínio", "pcc", "milícia"],
    "violencia": ["violência", "agressão", "assassinato", "morte violenta", "conflito", "tiroteio", "bala perdida"],
    "drogas": ["drogas", "tráfico", "entorpecentes", "maconha", "cocaína", "crack", "legalização", "guerra às drogas", "descriminalização"],
    "genero": ["gênero", "feminismo", "machismo", "igualdade de gênero", "mulher", "feminicídio", "empoderamento", "teto de vidro", "assédio"],
    "lgbtqia": ["lgbtqia", "lgbt", "gay", "trans", "homossexual", "identidade de gênero", "orientação sexual", "diversidade", "pride", "casamento igualitário"],
    "racial": ["racial", "racismo", "negro", "preto", "branco", "pardo", "cotas", "ações afirmativas", "discriminação", "colorismo", "branquitude"],
    "indigena": ["indígena", "indio", "demarcação", "terra indígena", "yanomami", "guarani", "funai", "marco temporal", "genocídio indígena"],
    "pcd": ["pcd", "deficiente", "acessibilidade", "inclusão", "libras", "braile", "autismo", "neurodivergente", "capacitismo"],
    "idosos": ["idoso", "envelhecimento", "aposentadoria", "previdência", "inatividade", "terceira idade", "geriatria", "cuidadores", "estatuto do idoso"],

    # Educação (10)
    "educacao": ["educação", "escola", "universidade", "ensino", "professor", "aluno", "enem", "faculdade", "mestrado", "doutorado", "analfabetismo", "pisa", "ideb", "fies", "prouni"],
    "ensino_superior": ["ensino superior", "universidade", "faculdade", "graduação", "mestrado", "doutorado", "pós-graduação", "capes", "cnpq", "universidade pública", "universidade privada"],
    "ciencia": ["ciência", "científico", "método científico", "laboratório", "pesquisa", "publicação", "peer review", "revisão por pares", "negacionismo"],
    "tecnologia": ["tecnologia", "tech", "digital", "internet", "software", "hardware", "app", "aplicativo", "startup", "código", "desenvolvimento"],
    "inovacao": ["inovação", "startup", "tecnologia", "pesquisa", "desenvolvimento", "patente", "empreendedor", "venture capital", "aceleradora", "hub", "disrupção"],
    "pesquisa_desenvolvimento": ["p&d", "pesquisa e desenvolvimento", "inovação", "cientista", "laboratório", "bolsa", "fomento", "finep", "embrapa"],
    "fuga_cerebros": ["fuga de cérebros", "brain drain", "emigração qualificada", "diáspora científica", "expatriado", "intercâmbio", "mobilidade acadêmica"],
    "ensino_tecnico": ["ensino técnico", "curso técnico", "senai", "senac", "profissionalizante", "formação profissional", "oficina", "aprendiz"],
    "educacao_infantil": ["educação infantil", "creche", "pré-escola", "alfabetização", "base curricular", "bncc", "primeira infância"],
    "alfabetizacao": ["alfabetização", "letramento", "leitura", "escrita", "analfabeto funcional", "método fônico", "educação básica"],

    # Saúde (10)
    "saude": ["saúde", "sus", "hospital", "médico", "vacina", "pandemia", "covid", "doença", "leito", "uti", "enfermeiro", "remédio", "farmacêutico", "emergência"],
    "saude_mental": ["saúde mental", "depressão", "ansiedade", "burnout", "transtorno", "terapia", "psicólogo", "psiquiatra", "suicídio", "bem-estar emocional"],
    "pandemia": ["pandemia", "covid", "coronavírus", "lockdown", "quarentena", "distanciamento social", "máscara", "variante", "onda", "surto"],
    "vacinas": ["vacina", "imunização", "vacinação", "pni", "butantan", "fiocruz", "antivacina", "imunidade", "reforço", "pfizer", "coronavac"],
    "dengue": ["dengue", "aedes", "mosquito", "chikungunya", "zika", "febre amarela", "endemia", "fumacê", "água parada"],
    "cancer": ["câncer", "tumor", "oncologia", "quimioterapia", "radioterapia", "mamografia", "próstata", "prevenção", "tabagismo", "hereditário"],
    "obesidade": ["obesidade", "sobrepeso", "sedentarismo", "alimentação saudável", "imc", "dieta", "exercício", "metabolismo", "cirurgia bariátrica"],
    "alcoolismo": ["álcool", "alcoolismo", "bebida", "cerveja", "cachaça", "dependência", "aa", "alcoólicos anônimos", "ressaca", "cirrose"],
    "tabagismo": ["tabaco", "cigarro", "fumo", "nicotina", "antitabagismo", "cigarro eletrônico", "vape", "pod", "dpoc", "pulmão"],
    "drogas_licitas": ["droga lícita", "medicamento", "remédio controlado", "ansiolítico", "opioide", "automedicação", "prescrição", "farmácia"],

    # Tecnologia (10)
    "ia_impacto": ["ia ", "inteligência artificial", "chatgpt", "gpt", "automação", "robô", "machine learning", "deep learning", "llm", "copilot", "gemini", "claude"],
    "ia_etica": ["ética ia", "viés algorítmico", "explicabilidade", "transparência", "accountability", "algoritmo justo", "discriminação algorítmica", "sesgo ia"],
    "ia_regulacao": ["regulação ia", "marco regulatório", "ai act", "regulamentação", "legislação", "sandbox regulatório", "conformidade", "compliance ia"],
    "automacao": ["automação", "robô", "rpa", "desemprego tecnológico", "fábrica automática", "indústria 4.0", "manufatura avançada"],
    "robotica": ["robótica", "robô", "drone", "veículo autônomo", "carro autônomo", "cirurgia robótica", "exoesqueleto"],
    "privacidade_dados": ["privacidade", "dados pessoais", "lgpd", "gdpr", "vigilância", "reconhecimento facial", "big data", "data broker", "cookies"],
    "ciberseguranca": ["cibersegurança", "hacker", "ransomware", "phishing", "vazamento", "ataque cibernético", "malware", "firewall", "criptografia"],
    "blockchain": ["blockchain", "bitcoin", "criptomoeda", "nft", "defi", "contrato inteligente", "tokenização", "web3", "descentralização", "mineração"],
    "metaverso": ["metaverso", "realidade virtual", "vr", "ar", "realidade aumentada", "avatar", "mundo virtual", "oculus", "apple vision"],
    "computacao_quantica": ["computação quântica", "qubit", "quantum", "ibm quantum", "supremacia quântica", "criptografia quântica", "emaranhamento"],

    # Meio Ambiente (10)
    "meio_ambiente": ["ambiente", "ecologia", "sustentável", "preservação", "conservação", "esg", "green", "eco", "natural", "poluição", "contaminação"],
    "amazonia": ["amazônia", "floresta", "desmatamento", "queimada", "madeireiro", "garimpo", "bioeconomia", "povos da floresta", "sumaúma"],
    "mudancas_climaticas": ["mudanças climáticas", "aquecimento global", "clima", "efeito estufa", "cop", "acordo de paris", "descarbonização", "net zero", "mitigação"],
    "energia_renovavel": ["energia renovável", "solar", "eólica", "hidrelétrica", "biomassa", "hidrogênio verde", "eólica offshore", "transição energética", "limpa"],
    "carbono": ["carbono", "co2", "emissão", "crédito de carbono", "mercado de carbono", "compensação", "sequestro", "pegada ecológica", "neutralidade"],
    "reciclagem": ["reciclagem", "lixo", "resíduo", "plástico", "descarte", "aterro", "economia circular", "compostagem", "logística reversa"],
    "agua": ["água", "recursos hídricos", "seca", "escassez", "crise hídrica", "aquífero", "irrigação", "bacia", "represa", "transposição"],
    "biodiversidade": ["biodiversidade", "extinção", "espécie", "fauna", "flora", "cerrado", "pantanal", "mata atlântica", "caatinga", "bioma"],
    "oceanos": ["oceano", "marinho", "plástico no mar", "acidificação", "corais", "pesca", "zona costeira", "petróleo no mar", "pré-sal", "corrente marítima"],
    "desastres_naturais": ["desastre natural", "enchente", "inundação", "deslizamento", "terremoto", "tsunami", "furacão", "seca", "incêndio florestal", "tragédia"],

    # Geopolítica (10)
    "guerra": ["guerra", "conflito armado", "invasão", "ocupação", "bombardeio", "frente de batalha", "exército", "artilharia", "baixas", "combate"],
    "paz": ["paz", "cessar-fogo", "trégua", "acordo de paz", "diplomacia", "negociação", "mediação", "desarmamento", "reconciliação"],
    "conflitos": ["conflito", "disputa", "tensão", "hostilidade", "escalada", "ameaça", "ultimato", "embargo", "ruptura", "crise"],
    "refugiados": ["refugiado", "asilo", "acnur", "deslocado", "migrante", "campo de refugiados", "crise humanitária", "acolhimento", "xenofobia"],
    "imigracao": ["imigração", "imigrante", "fronteira", "visto", "residência", "naturalização", " deportação", "trabalhador migrante", "brain gain"],
    "nacionalismo": ["nacionalismo", "patriotismo", "soberania", "nação", "identidade nacional", "hino", "bandeira", "ufanismo", "chauvinismo"],
    "globalizacao": ["globalização", "interdependência", "transnacional", "multilateralismo", "cadeia global", "world economy", "cosmopolitismo", "aldeia global"],
    "blocos_economicos": ["bloco econômico", "mercosul", "união europeia", "brics", "g20", "g7", "usmca", "aliança do pacífico", "zona de livre comércio"],
    "otan": ["otan", "nato", "aliança militar", "artigo 5", "defesa coletiva", "dissuasão", "expansão otan", "escudo antimísseis"],
    "onu": ["onu", "nações unidas", "conselho de segurança", "assembleia geral", "unesco", "oms", "acnur", "peacekeeping", "direitos humanos", "veto"],

    # Política (10)
    "eleicoes": ["eleição", "voto", "urna", "candidato", "campanha", "debate", "pleito", "sufrágio", "comparecimento", "abstenção", "segundo turno"],
    "corrupcao": ["corrupção", "propina", "desvio", "lavagem", "lava jato", "mensalão", "petrolão", "superfaturamento", "rachadinha", "orçamento secreto"],
    "transparencia": ["transparência", "accountability", "prestação de contas", "portal transparência", "lei acesso informação", "dados abertos", "controle social"],
    "reforma_politica": ["reforma política", "voto distrital", "distritão", "fim reeleição", "cláusula barreira", "financiamento campanha", "fundão", "partido"],
    "democracia": ["democracia", "liberdade", "estado de direito", "constituição", "divisão poderes", "checks and balances", "golpe", "ditadura", "transição"],
    "autoritarismo": ["autoritarismo", "ditadura", "autocracia", "repressão", "censura", "perseguição", "oposição", "dissidente", "prisão política"],
    "populismo": ["populismo", "populista", "demagogia", "plebiscito", "povo", "elite", "pão e circo", "messianismo", "caudilhismo"],
    "fake_news": ["fake news", "desinformação", "notícia falsa", "boato", "checagem", "fact-checking", "pós-verdade", "deep fake", "zap zap"],
    "liberdade_imprensa": ["liberdade de imprensa", "jornalismo", "repórter", "censura", "mídia", "imprensa livre", "lei de imprensa", "concessão", "tv pública"],
    "participacao_popular": ["participação", "plebiscito", "referendo", "iniciativa popular", "conselho", "orçamento participativo", "audiência pública", "consulta"],

    # Cultura & Comportamento (10)
    "cultura": ["cultura", "arte", "música", "cinema", "teatro", "literatura", "museu", "patrimônio", "folclore", "carnaval", "festa popular"],
    "religiao": ["religião", "fé", "deus", "igreja", "evangélico", "católico", "espírita", "umbanda", "candomblé", "ateu", "laicidade", "intolerância religiosa"],
    "esporte": ["esporte", "futebol", "olimpíadas", "copa", "atleta", "campeonato", "torcida", "estádio", "basquete", "mma", "volei"],
    "entretenimento": ["entretenimento", "streaming", "netflix", "youtube", "tiktok", "filme", "série", "show", "show", "podcast", "influencer"],
    "redes_sociais": ["redes sociais", "instagram", "twitter", "facebook", "tiktok", "linkedin", "whatsapp", "telegram", "algoritmo", "engajamento", "like"],
    "saude_mental_publica": ["saúde mental pública", "caps", "rap", "atenção psicossocial", "reforma psiquiátrica", "medicalização", "antidepressivo", "lítio"],
    "burnout": ["burnout", "esgotamento", "estafa", "exaustão", "estresse crônico", "síndrome", "excesso trabalho", "descanso", "desconexão", "férias"],
    "nomadismo_digital": ["nômade digital", "trabalho remoto", "home office", "coworking", "anywhere office", "trabalhar viajando", "visto nômade", "freelancer global"],
    "minimalismo": ["minimalismo", "menos é mais", "desapego", "consumo consciente", "essencialismo", "simplicidade voluntária", "anticonsumo", "slow living"],
    "consumismo": ["consumismo", "consumo", "compra", "shopping", "publicidade", "marketing", "black friday", "cartão de crédito", "endividamento", "supérfluo"],
}

EMOTION_LEXICON = {
    "positive": ["😊", "😄", "😍", "❤", "💚", "🎉", "🥳", "🙌", "👏", "💪", "🔥", "✨", "☀️", "😁", "🤩", "😎"],
    "negative": ["😢", "😡", "🤬", "💔", "😤", "👎", "😭", "😩", "😫", "😠", "🤮", "💀", "😱", "🤯", "😰", "😨"],
}


class WhatsAppProfiler:
    """Analisa chat do WhatsApp e extrai perfis cognitivos."""

    def __init__(self, chat_path: str = None):
        self.chat_path = chat_path
        self.messages: List[Dict] = []
        self.profiles: Dict[str, Dict] = {}
        self.group_stats: Dict[str, Any] = {}

    def parse_chat(self, text: str) -> List[Dict]:
        """Parseia arquivo de chat WhatsApp exportado (.txt)."""
        messages = []
        current_msg = None

        for line in text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue

            # Tenta padrão BR
            m = RE_BR.match(line)
            if not m:
                m = RE_INTL.match(line)
            if not m:
                m = RE_SYSTEM.match(line)

            if m:
                if current_msg:
                    messages.append(current_msg)
                date_str, time_str, sender, content = m.group(1), m.group(2), m.group(3).strip(), m.group(4).strip()

                # Normaliza data
                try:
                    for fmt in ["%d/%m/%Y", "%m/%d/%Y", "%d/%m/%y", "%m/%d/%y"]:
                        try:
                            dt = datetime.strptime(f"{date_str} {time_str.split(',')[0].strip().upper().replace(' AM','').replace(' PM','')}", f"{fmt} %H:%M")
                            break
                        except ValueError:
                            continue
                    else:
                        dt = datetime.now(BRAZIL_TZ)
                except:
                    dt = datetime.now(BRAZIL_TZ)

                current_msg = {
                    "datetime": dt.isoformat(),
                    "sender": sender,
                    "content": content,
                    "is_media": bool(RE_MEDIA.search(content)),
                    "is_system": bool(RE_SYSTEM_MSG.search(line)),
                }
            else:
                # Continuação de mensagem anterior (multilinha)
                if current_msg and not current_msg.get("is_system"):
                    current_msg["content"] += " " + line

        if current_msg:
            messages.append(current_msg)

        self.messages = [m for m in messages if not m.get("is_system") and not m.get("is_media")]
        return self.messages

    def parse_json(self, data: List[Dict]) -> List[Dict]:
        """Parseia saída JSON do whatsapp-mcp."""
        self.messages = []
        for item in data:
            self.messages.append({
                "datetime": item.get("timestamp", item.get("datetime", "")),
                "sender": item.get("sender", item.get("from", item.get("author", "?"))),
                "content": item.get("content", item.get("body", item.get("text", ""))),
                "is_media": item.get("is_media", False),
                "is_system": False,
            })
        return self.messages

    def load_file(self, path: str) -> List[Dict]:
        """Carrega arquivo (txt ou json)."""
        self.chat_path = path
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        if path.endswith('.json'):
            data = json.loads(content)
            if isinstance(data, list):
                return self.parse_json(data)
            elif isinstance(data, dict) and 'messages' in data:
                return self.parse_json(data['messages'])

        return self.parse_chat(content)

    def build_profiles(self) -> Dict[str, Dict]:
        """Constrói perfis cognitivos a partir das mensagens."""
        if not self.messages:
            return {}

        # Agrupar por sender
        by_sender = defaultdict(list)
        for msg in self.messages:
            sender = msg["sender"].strip()
            if sender and len(sender) > 1:
                by_sender[sender].append(msg)

        profiles = {}
        all_senders = list(by_sender.keys())
        total_msgs = len(self.messages)

        for sender, msgs in by_sender.items():
            msg_count = len(msgs)
            if msg_count < 3:
                continue

            # ── 1. Análise de stance ──
            stance_scores = defaultdict(int)
            for msg in msgs:
                content_lower = msg["content"].lower()
                for stance, keywords in STANCE_KEYWORDS.items():
                    for kw in keywords:
                        if kw in content_lower:
                            stance_scores[stance] += 1

            dominant_stance = max(stance_scores, key=stance_scores.get) if stance_scores else "neutral"
            stance_confidence = min(stance_scores[dominant_stance] / max(msg_count * 0.3, 1), 1.0)

            # ── 2. Análise de tópicos ──
            topic_scores = defaultdict(int)
            for msg in msgs:
                content_lower = msg["content"].lower()
                for topic, keywords in TOPIC_KEYWORDS.items():
                    for kw in keywords:
                        if kw in content_lower:
                            topic_scores[topic] += 1

            top_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)[:3]

            # ── 3. Análise de sentimento ──
            sentiment_total = 0.0
            emotion_count = 0
            for msg in msgs:
                content = msg["content"]
                pos = sum(1 for e in EMOTION_LEXICON["positive"] if e in content)
                neg = sum(1 for e in EMOTION_LEXICON["negative"] if e in content)
                if pos + neg > 0:
                    sentiment_total += (pos - neg) / (pos + neg)
                    emotion_count += 1

            avg_sentiment = round(sentiment_total / max(emotion_count, 1), 3)

            # ── 4. Métricas de engajamento ──
            word_counts = [len(msg["content"].split()) for msg in msgs if msg.get("content")]
            avg_words = round(sum(word_counts) / max(len(word_counts), 1), 1)

            # Verificar horários de atividade
            hours = []
            for msg in msgs:
                try:
                    dt = datetime.fromisoformat(msg["datetime"])
                    hours.append(dt.hour)
                except:
                    pass

            # ── 5. Influência no grupo ──
            # Mensagens que geraram resposta (alguém respondeu em até 10 min)
            responses_generated = 0
            msgs_sorted = sorted(msgs, key=lambda m: m.get("datetime", ""))
            for i, msg in enumerate(msgs_sorted):
                try:
                    dt = datetime.fromisoformat(msg["datetime"])
                    for j in range(i + 1, min(i + 5, len(msgs_sorted))):
                        try:
                            next_dt = datetime.fromisoformat(msgs_sorted[j]["datetime"])
                            if (next_dt - dt).total_seconds() < 600:
                                responses_generated += 1
                                break
                        except:
                            pass
                except:
                    pass

            influence = round(
                (msg_count / total_msgs) * 0.3 +
                (responses_generated / max(msg_count, 1)) * 0.4 +
                (avg_words / 200) * 0.3, 3
            )

            # ── Montar perfil ──
            profile = {
                "name": sender,
                "message_count": msg_count,
                "avg_words_per_msg": avg_words,
                "dominant_stance": dominant_stance,
                "stance_confidence": round(stance_confidence, 3),
                "stance_scores": dict(stance_scores),
                "top_topics": [{"topic": t, "score": s} for t, s in top_topics],
                "avg_sentiment": avg_sentiment,
                "influence": min(influence, 1.0),
                "responses_generated": responses_generated,
                "active_hours": sorted(set(hours)) if hours else [],
                "cognitive_style": self._infer_cognitive_style(msg_count, avg_words, dominant_stance, avg_sentiment),
            }
            profiles[sender] = profile

        self.profiles = profiles
        self._compute_group_stats()
        return profiles

    def _infer_cognitive_style(self, msg_count: int, avg_words: float,
                                stance: str, sentiment: float) -> str:
        """Infere estilo cognitivo do perfil."""
        if msg_count > 50 and avg_words > 50:
            base = "Analítico-Argumentativo"
        elif msg_count > 20 and avg_words > 20:
            base = "Reflexivo-Discursivo"
        elif stance == "curious":
            base = "Investigativo-Inquisitivo"
        elif msg_count > 30:
            base = "Reativo-Engajado"
        else:
            base = "Observador-Pontual"

        if sentiment > 0.2:
            base += " (Otimista)"
        elif sentiment < -0.2:
            base += " (Crítico)"
        else:
            base += " (Neutro)"
        return base

    def _compute_group_stats(self):
        """Calcula estatísticas agregadas do grupo."""
        if not self.profiles:
            return

        profiles = list(self.profiles.values())
        self.group_stats = {
            "total_members": len(profiles),
            "total_messages": len(self.messages),
            "member_count": len(profiles),
            "stance_distribution": {
                s: sum(1 for p in profiles if p["dominant_stance"] == s)
                for s in ["supportive", "critical", "curious", "neutral"]
            },
            "avg_sentiment": round(sum(p["avg_sentiment"] for p in profiles) / len(profiles), 3),
            "top_influencers": sorted(
                [{"name": p["name"], "influence": p["influence"]} for p in profiles],
                key=lambda x: x["influence"], reverse=True
            )[:5],
            "dominant_topics": self._aggregate_topics(profiles),
            "cognitive_diversity": len(set(p["cognitive_style"] for p in profiles)) / max(len(profiles), 1),
        }

    def _aggregate_topics(self, profiles: List[Dict]) -> List[Dict]:
        """Agrega tópicos mais frequentes entre membros."""
        topic_total = Counter()
        for p in profiles:
            for t in p.get("top_topics", []):
                topic_total[t["topic"]] += t["score"]
        return [{"topic": t, "members": c} for t, c in topic_total.most_common(10)]

    def to_sim_agents(self) -> List[Dict]:
        """Converte perfis em SimAgent profiles para o sim_engine."""
        agents = []
        for name, profile in self.profiles.items():
            agents.append({
                "name": name,
                "labels": [profile.get("cognitive_style", "observador")],
                "activity_config": {
                    "activity_level": min(profile["message_count"] / 100, 1.0),
                    "influence_weight": profile["influence"] * 3.0,
                    "stance": profile["dominant_stance"],
                    "sentiment_bias": profile["avg_sentiment"],
                    "posts_per_hour": profile["message_count"] / 24,
                }
            })
        return agents

    def map_to_expanded_profiles(self) -> Dict[str, Dict]:
        """
        Mapeia cada perfil WhatsApp para o arquétipo psicológico expandido mais próximo.
        Usa correspondência por stance + estilo cognitivo + volume de mensagens.
        """
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                "..", "..", "simulation-runner", "scripts"))
            from expanded_profiles import EXPANDED_PROFILES
        except ImportError:
            return {}

        mapping = {}
        for name, profile in self.profiles.items():
            stance = profile["dominant_stance"]
            style = profile["cognitive_style"]
            msg_count = profile["message_count"]

            # Filtrar candidatos por stance compatível
            candidates = [p for p in EXPANDED_PROFILES if p["stance"] == stance]

            if not candidates:
                candidates = [p for p in EXPANDED_PROFILES if p["stance"] in ("neutral", stance)]

            # Rank por afinidade de estilo cognitivo
            cognitive_map = {
                "Analítico-Argumentativo": ["analitico", "cientifico", "estrategico"],
                "Reflexivo-Discursivo": ["analitico", "cientifico", "ideologico"],
                "Investigativo-Inquisitivo": ["cientifico", "analitico", "comunicador"],
                "Reativo-Engajado": ["social", "emocional", "comunicador"],
                "Observador-Pontual": ["analitico", "comportamental", "regional"],
            }

            preferred_cats = cognitive_map.get(
                style.split(" (")[0] if "(" in style else style,
                ["analitico"]
            )

            scored = []
            for ep in candidates:
                score = 0
                if ep["category"] in preferred_cats: score += 3
                if ep["category"] == preferred_cats[0]: score += 2
                # Big Five: preferir match de Amabilidade para supportive, Neuroticismo para critical
                bf = ep.get("big_five", {})
                if stance == "supportive" and bf.get("A", 0) > 0.6: score += 1
                if stance == "critical" and bf.get("N", 0) > 0.4: score += 1
                # Alta contagem de msgs → perfis mais influentes
                if msg_count > 100 and ep["category"] in ("social", "comunicador", "estrategico"): score += 1
                scored.append((score, ep))

            scored.sort(key=lambda x: x[0], reverse=True)

            # Top 3 matches
            top_matches = []
            for score, ep in scored[:3]:
                top_matches.append({
                    "profile_id": ep["id"],
                    "profile_name": ep["name"],
                    "category": ep["category"],
                    "match_score": score,
                    "description": ep.get("description", ""),
                    "references": ep.get("references", []),
                    "cognitive": ep.get("cognitive", ""),
                    "psychological_dimensions": {
                        "big_five": ep.get("big_five", {}),
                        "schwartz": ep.get("schwartz", []),
                        "moral": ep.get("moral", []),
                        "regulatory": ep.get("regulatory", ""),
                        "dark_triad": ep.get("dark_triad", ""),
                        "attachment": ep.get("attachment", ""),
                        "locus": ep.get("locus", ""),
                        "rwa": ep.get("rwa", ""),
                        "sdo": ep.get("sdo", ""),
                    },
                })

            mapping[name] = {
                "whatsapp_profile": profile,
                "top_matches": top_matches,
                "best_match": top_matches[0] if top_matches else None,
                "confidence": "alta" if top_matches and top_matches[0]["match_score"] >= 4 else "media",
            }

        return mapping

    def export_profiles(self, path: str = None) -> str:
        """Exporta perfis para JSON."""
        if path is None:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", ".reversa", "whatsapp_profiles.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        export = {
            "source": self.chat_path,
            "profiled_at": datetime.now(BRAZIL_TZ).isoformat(),
            "group_stats": self.group_stats,
            "profiles": self.profiles,
            "sim_agents": self.to_sim_agents(),
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(export, f, indent=2, ensure_ascii=False)
        return path

    def generate_report(self) -> str:
        """Gera relatório textual dos perfis do grupo."""
        if not self.profiles:
            return "Nenhum perfil extraído."

        gs = self.group_stats
        lines = [
            f"# 📱 Perfil Cognitivo do Grupo WhatsApp",
            f"",
            f"**Membros analisados:** {gs['total_members']}",
            f"**Mensagens processadas:** {gs['total_messages']}",
            f"**Diversidade cognitiva:** {gs['cognitive_diversity']:.1%}",
            f"**Sentimento médio:** {gs['avg_sentiment']:+.3f}",
            f"",
            f"## Distribuição de Stances",
        ]
        for stance, count in gs["stance_distribution"].items():
            pct = count / max(gs["total_members"], 1) * 100
            lines.append(f"- **{stance}:** {count} membros ({pct:.0f}%)")

        lines.append(f"\n## Top Influenciadores")
        for i, inf in enumerate(gs["top_influencers"][:5], 1):
            lines.append(f"{i}. **{inf['name']}** — influência: {inf['influence']:.3f}")

        lines.append(f"\n## Perfis Individuais")
        for name, p in sorted(self.profiles.items(), key=lambda x: x[1]["message_count"], reverse=True):
            lines.append(f"\n### {name}")
            lines.append(f"- Mensagens: {p['message_count']} | Média palavras: {p['avg_words_per_msg']}")
            lines.append(f"- Stance: **{p['dominant_stance']}** (confiança: {p['stance_confidence']:.0%})")
            lines.append(f"- Sentimento: {p['avg_sentiment']:+.3f}")
            lines.append(f"- Influência: {p['influence']:.3f} | Estilo: {p['cognitive_style']}")
            if p["top_topics"]:
                lines.append(f"- Tópicos: {', '.join(t['topic'] for t in p['top_topics'][:3])}")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# CLI / Demo
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Demo com dados sintéticos
    print("═" * 60)
    print("📱 WhatsApp Cognitive Profiler — Demo")
    print("═" * 60)

    sample_chat = """
14/01/2025 09:15 - Ana: Bom dia! Viram a notícia sobre a nova IA do Google?
14/01/2025 09:17 - Bruno: Sim! Achei sensacional. Isso vai revolucionar a educação.
14/01/2025 09:20 - Carla: Discordo. Automatizar tudo vai aumentar o desemprego e a desigualdade.
14/01/2025 09:22 - Diego: Qual a fonte dessa notícia? Me manda o link?
14/01/2025 09:25 - Ana: https://blog.google/technology/ai/gemini-update-2025/
14/01/2025 09:30 - Bruno: Exatamente, Ana. Os dados mostram que países que investem em IA crescem mais.
14/01/2025 09:33 - Carla: Mas a que custo social? A desigualdade no Brasil já é enorme.
14/01/2025 09:35 - Diego: Interessante. Vocês já viram o paper do Acemoglu sobre automação?
14/01/2025 09:38 - Ester: Concordo com a Carla. Precisamos pensar nos impactos sociais primeiro. 😤
14/01/2025 09:40 - Bruno: Mas sem inovação não tem crescimento. O Brasil investe só 1.2% do PIB em P&D.
14/01/2025 09:42 - Ana: Acho que os dois lados têm razão. Precisamos de equilíbrio. 🤔
14/01/2025 09:45 - Diego: Faz sentido. Inovação com regulação social pode ser o caminho.
14/01/2025 09:48 - Carla: Só acredito vendo. O histórico de promessas tech não é bom. 😒
14/01/2025 09:50 - Bruno: Discordo totalmente. Quem não inova fica pra trás.
14/01/2025 09:52 - Ester: Vocês dois são muito 8 ou 80. Existe meio termo, gente! 😂
14/01/2025 09:55 - Ana: Proponho a gente fazer um grupo de estudo sobre isso.
14/01/2025 10:00 - Diego: Ótima ideia, Ana! Eu organizo o material. 🎉
14/01/2025 10:05 - Carla: Ok, vou participar. Mas mantenho minhas críticas.
14/01/2025 10:08 - Bruno: Fechado! Vamos estudar juntos. 👏
14/01/2025 10:10 - Ester: Adorei a iniciativa! ❤️
"""

    profiler = WhatsAppProfiler()
    profiler.parse_chat(sample_chat)
    profiles = profiler.build_profiles()

    print(f"\nMensagens: {len(profiler.messages)}")
    print(f"Perfis extraídos: {len(profiles)}")
    print(f"Diversidade cognitiva: {profiler.group_stats.get('cognitive_diversity', 0):.1%}")

    for name, p in sorted(profiles.items(), key=lambda x: x[1]["message_count"], reverse=True):
        print(f"\n  {name}: {p['message_count']} msgs | stance={p['dominant_stance']} "
              f"| sent={p['avg_sentiment']:+.2f} | style={p['cognitive_style']}")

    path = profiler.export_profiles()
    print(f"\n✅ Perfis exportados: {path}")
    print(f"   SimAgent profiles: {len(profiler.to_sim_agents())} agentes prontos para simulação")
